import logging
import time
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser


from src.api.exceptions import KnowledgeBaseException, LLMException, ValidationException
from src.memory.conversation_memory import ConversationMemory
from src.core.hybrid_retriever import hybrid_search
from src.services.llm import create_llm
from src.services.prompts import RAG_PROMPT, QUERY_REWRITE_PROMPT
from src.settings import settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service responsible for executing the complete
    Retrieval-Augmented Generation (RAG) pipeline.
    """

    def __init__(self):
        """
        Initialize all components required for the RAG pipeline.
        """

        logger.info("=" * 70)
        logger.info("Initializing RAG Service...")
        logger.info("=" * 70)

        try:

            # Initialize LLM
            self.llm = create_llm()
            logger.info("LLM initialized successfully.")

            # Initialize Output Parser
            self.output_parser = StrOutputParser()

            self.memory = ConversationMemory(
                max_messages=settings.max_history_messages,
            )
            logger.info("Output parser initialized successfully.")

            logger.info("RAG pipeline created successfully.")
            logger.info("=" * 70)

        except Exception:
            logger.exception("Failed to initialize RAG Service.")
            raise

    @staticmethod
    def create_preview(text: str, limit: int = 200) -> str:
        """
        Return a shortened preview of text for logging.
        """

        if len(text) <= limit:
            return text

        return text[:limit] + "..."

    def calculate_confidence(
        self,
        distance: float,
    ) -> float:
        """
        Convert retrieval distance into a confidence score.

        Distance:
            0.00 -> perfect match
            1.00 -> weak match

        Confidence is estimated from the retriever's distance score.

        It is intended as a heuristic to indicate how well the retrieved
        documents match the user's query. It is not a calibrated probability.
        """

        confidence = round(
            1 / (1 + distance),
            2,
        )

        return confidence


    @staticmethod
    def format_docs(docs):
        """
        Convert  retrieved documents into a single context string that will be sent to LLM

        """
        logger.info(
    "Retrieved %d relevant chunks",
    len(docs),
)

        for index, doc in enumerate(docs, start=1):

            logger.info("-" * 60)
            logger.info("Document %d", index)
            logger.info("Source: %s", doc.metadata.get("source", "Unknown"))

            logger.info(
                "Preview : %s",
                RAGService.create_preview(doc.page_content.replace("\n", " ")),
            )
        logger.info("-" * 60)

        context = "\n\n".join(doc.page_content for doc in docs)

        return context

    def ask(self, question: str) -> dict:
        """
        Execute the complete RAG pipeline.

        Parameters
        ----------
        question : str
            User's natural language question.

        Returns
        -------
        str
            Generated answer from the LLM.
        """

        logger.info("=" * 70)
        logger.info("NEW RAG REQUEST")
        logger.info("=" * 70)

        logger.info("Question : %s", question)

        if not isinstance(question, str):
            logger.warning(
                "Invalid question type received: %s",
                type(question).__name__,
            )
            raise ValidationException("Question must be a string.")

            question = question.strip()

            if not question:
                logger.warning("Empty or whitespace-only question received.")
                raise ValidationException("Question cannot be empty.")

        start_time = time.perf_counter()

        retrieval_start = time.perf_counter()

        logger.info("Question Length : %d characters", len(question))

        logger.info("Stage 1 : Retrieving relevant documents...")

        try:
            retrieval_query = self.rewrite_query(question)

        except LLMException:
            raise

        except Exception as error:
            logger.exception("Query rewriting failed.")
            raise LLMException(
                "Unable to rewrite the query."
            ) from error

        try:
            documents = hybrid_search(
                retrieval_query,
                top_k=settings.top_k,
            )

            source_pages = {}

            for document in documents:
                source = document.metadata.get("source")
                page = document.metadata.get("page_label")

                if source is None:
                    continue

                filename = document.metadata.get("filename")

                if filename not in source_pages:
                    source_pages[filename] = set()

                source_pages[filename].add(page)

            logger.info("Retrieved Sources: %s", source_pages)
            logger.info("Relevance gate passed.")

        except Exception as error:
            logger.exception(
                "Stage 1 failed while retrieving documents."
            )
            raise KnowledgeBaseException(
                "Unable to retrieve documents."
            ) from error

        if not documents:
            logger.warning(
                "No relevant documents found for the question."
            )

            logger.info(
                "RAG request completed without a knowledge-base match."
            )

            return {
                "answer": (
                    "I couldn't find any relevant information "
                    "in the uploaded documents."
                ),
                "citations": [],
                "metadata": {
                    "retrieved_documents": 0,
                    "llm_model": settings.llm_model,
                    "embedding_model": settings.embedding_model,
                },
            }


        retrieval_end = time.perf_counter()

        retrieval_time = retrieval_end - retrieval_start


        # raise RuntimeError("Unexpected bug")
        context = self.format_docs(documents)
        logger.info("Context created successfully (%d characters).", len(context))


        logger.info("Stage 2 : Creating prompt...")

        history = self.memory.get_history()
        prompt_start = time.perf_counter()

        prompt = RAG_PROMPT.invoke({"history": history,"context": context, "question": question})

        prompt_end = time.perf_counter()

        prompt_time = prompt_end - prompt_start



        logger.info("Stage 2 completed successfully.")
        logger.info("=" * 70)
        logger.info("PROMPT SENT TO THE LLM")
        logger.info("=" * 70)

        if settings.log_full_prompt:

            logger.info(prompt.to_string())

        else:

            logger.info("Prompt Length : %d characters", len(prompt.to_string()))

        logger.info("=" * 70)

        logger.info("Stage 3: Invoking LLM...")

        llm_start_time = time.perf_counter()

        try:
            # raise Exception("Testing LLM Failure")
            response = self.llm.invoke(prompt)

        except Exception as error:

            logger.exception("Stage 3 failed while invoking the LLM.")

            raise LLMException("Unable to generate response.") from error

        logger.info("Stage 4 : Parsing LLM response...")

        parse_start = time.perf_counter()

        try:
            answer = self.output_parser.invoke(response)

        except Exception as error:
            logger.exception(
                "Stage 4 failed while parsing the LLM response."
            )
            raise LLMException(
                "Unable to process the generated response."
            ) from error

        self.memory.add_user_message(question)
        self.memory.add_ai_message(answer)
        answer_length = len(answer)
        word_count = len(answer.split())
        line_count = len(answer.splitlines())
        source_count = len(source_pages)
        chunk_count = len(documents)

        parse_end = time.perf_counter()

        parse_time = parse_end - parse_start


        logger.info("Answer Preview : %s", self.create_preview(answer))



        logger.info("=" * 70)

        logger.info("LLM response parsed successfully.")

        logger.info("=" * 70)
        logger.info("RESPONSE METADATA")
        logger.info("=" * 70)

        logger.info("Characters : %d", answer_length)
        logger.info("Words      : %d", word_count)
        logger.info("Lines      : %d", line_count)
        logger.info("Sources    : %d", source_count)
        logger.info("Chunks Used: %d", chunk_count)

        logger.info("=" * 70)

        llm_end_time = time.perf_counter()

        logger.info("RAG pipeline completed successfully.")

        end_time = time.perf_counter()

        total_time = end_time - start_time

        logger.info("=" * 70)
        logger.info("RAG PERFORMANCE SUMMARY")
        logger.info("=" * 70)

        logger.info("Retrieval       : %.3f s", retrieval_time)
        logger.info("Prompt Build    : %.3f s", prompt_time)
        logger.info("LLM Inference   : %.3f s", llm_end_time - llm_start_time)
        logger.info("Response Parse  : %.3f s", parse_time)
        logger.info("-" * 70)
        logger.info("Total Time      : %.3f s", total_time)
        logger.info("=" * 70)


        citation_set = set()
        citations = []

        for document in documents:
            source = document.metadata.get("source")
            page = document.metadata.get("page_label")

            if source is None or page is None:
                continue

            citation_set.add(
                (
                    Path(source).name,
                    int(page),
                )
            )

        citations = [
            {
                "file": file,
                "page": page,
            }
            for file, page in sorted(citation_set)
        ]


        logger.info("=" * 70)
        logger.info("Conversation History")
        logger.info("=" * 70)

        if history:
            logger.info("\n%s", history)
        else:
            logger.info("No previous conversation.")

        return {
            "answer": answer,
            # "confidence": confidence,
            "citations": citations,
            "metadata": {
                "retrieved_documents": len(documents),
                # "retrieval_distance": round(best_distance, 4),
                "llm_model": settings.llm_model,
                "embedding_model": settings.embedding_model,
            },
        }


    def rewrite_query(self, question: str) -> str:


        history = self.memory.get_history()

        if not history:
            return question

        prompt = QUERY_REWRITE_PROMPT.invoke(
            {
                "history": history,
                "question": question,
            }
        )

        try:
            rewritten_query = self.llm.invoke(prompt)
            rewritten_query = self.output_parser.invoke(rewritten_query)

        except Exception as error:
            logger.exception(
                "Query rewriting failed during LLM processing."
            )
            raise LLMException(
                "Unable to rewrite the query."
            ) from error

        logger.info("=" * 70)
        logger.info("QUERY REWRITE")
        logger.info("Original  : %s", question)
        logger.info("Rewritten : %s", rewritten_query)
        logger.info("=" * 70)

        logger.info("Rewritten Query : %s", rewritten_query)

        return rewritten_query.strip()


if __name__ == "__main__":

    rag = RAGService()

    while True:

        question = input("\nEnter your question (or 'exit'): ")

        if question.lower() == "exit":
            break

        response = rag.ask(question)

        print("\nAnswer:")
        print(response["answer"])
