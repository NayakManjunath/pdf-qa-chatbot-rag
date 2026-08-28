import logging
import time
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser

from src.api.exceptions import (
    KnowledgeBaseException,
    LLMException,
    ValidationException,
)
from src.core.hybrid_retriever import hybrid_search_with_scores
from src.memory.conversation_memory import ConversationMemory
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
        """Initialize all components required for the RAG pipeline."""

        logger.info("=" * 70)
        logger.info("Initializing RAG Service...")
        logger.info("=" * 70)

        try:
            # --------------------------------------------------
            # LLM
            # --------------------------------------------------

            self.llm = create_llm()
            logger.info("LLM initialized successfully.")

            # --------------------------------------------------
            # Output Parser
            # --------------------------------------------------

            self.output_parser = StrOutputParser()
            logger.info("Output parser initialized successfully.")

            # --------------------------------------------------
            # Conversation Memory
            # --------------------------------------------------

            self.memory = ConversationMemory(
                max_messages=settings.max_history_messages,
            )
            logger.info("Conversation memory initialized successfully.")

            logger.info("RAG pipeline created successfully.")
            logger.info("=" * 70)

        except Exception:
            logger.exception("Failed to initialize RAG Service.")
            raise

    # ==========================================================
    # Utility Methods
    # ==========================================================

    @staticmethod
    def create_preview(
        text: str,
        limit: int = 200,
    ) -> str:
        """Return a shortened preview of text for logging."""

        if len(text) <= limit:
            return text

        return text[:limit] + "..."

    def calculate_confidence(
        self,
        score: float,
    ) -> float:
        """
        Convert the reranker score into a normalized confidence score.

        This is a heuristic confidence score, not a calibrated probability.
        """

        import math

        try:
            score = float(score)
        except (TypeError, ValueError):
            return 0.0

        confidence = 1.0 / (1.0 + math.exp(-score))

        return round(
            min(max(confidence, 0.0), 1.0),
            2,
        )

    @staticmethod
    def format_docs(docs) -> str:
        """
        Convert retrieved documents into a single context string.
        """

        logger.info(
            "Retrieved %d relevant chunks.",
            len(docs),
        )

        for index, doc in enumerate(docs, start=1):
            logger.info("-" * 60)
            logger.info("Document %d", index)

            logger.info(
                "Source: %s",
                doc.metadata.get(
                    "source",
                    doc.metadata.get("filename", "Unknown"),
                ),
            )

            logger.info(
                "Preview: %s",
                RAGService.create_preview(
                    doc.page_content.replace("\n", " "),
                ),
            )

        logger.info("-" * 60)

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    # ==========================================================
    # Main RAG Pipeline
    # ==========================================================

    def ask(self, question: str) -> dict:
        """
        Execute the complete RAG pipeline.

        The pipeline is explicitly timed so that latency can be
        profiled stage by stage without changing the underlying
        retrieval or generation logic.
        """

        logger.info("=" * 70)
        logger.info("NEW RAG REQUEST")
        logger.info("=" * 70)

        logger.info("Question: %s", question)

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not isinstance(question, str):
            logger.warning(
                "Invalid question type received: %s",
                type(question).__name__,
            )

            raise ValidationException(
                "Question must be a string."
            )

        question = question.strip()

        if not question:
            logger.warning(
                "Empty or whitespace-only question received."
            )

            raise ValidationException(
                "Question cannot be empty."
            )

        total_start = time.perf_counter()

        logger.info(
            "Question Length: %d characters",
            len(question),
        )

        # ==================================================
        # Stage 1A: Query Rewriting
        # ==================================================

        logger.info("Stage 1A: Query rewriting...")

        rewrite_start = time.perf_counter()

        try:
            retrieval_query = self.rewrite_query(question)

        except LLMException:
            raise

        except Exception as error:
            logger.exception(
                "Query rewriting failed."
            )

            raise LLMException(
                "Unable to rewrite the query."
            ) from error

        rewrite_time = (
            time.perf_counter()
            - rewrite_start
        )

        logger.info(
            "Query rewriting completed in %.3f s.",
            rewrite_time,
        )

        # ==================================================
        # Stage 1B: Hybrid Retrieval
        # ==================================================

        logger.info("Stage 1B: Hybrid retrieval...")

        retrieval_start = time.perf_counter()

        try:
            reranked_results = hybrid_search_with_scores(
                retrieval_query,
                top_k=settings.top_k,
            )

            documents = [
                document
                for document, _score in reranked_results
            ]

            best_reranker_score = (
                reranked_results[0][1]
                if reranked_results
                else 0.0
            )

            confidence = self.calculate_confidence(
                best_reranker_score
            )

            logger.info(
                "Confidence Score: %.2f",
                confidence,
            )

            source_pages = {}

            for document in documents:
                filename = document.metadata.get(
                    "filename"
                )

                page = document.metadata.get(
                    "page_label"
                )

                if filename is None:
                    continue

                if filename not in source_pages:
                    source_pages[filename] = set()

                if page is not None:
                    source_pages[filename].add(page)

            logger.info(
                "Retrieved Sources: %s",
                source_pages,
            )

            logger.info("Relevance gate passed.")

        except Exception as error:
            logger.exception(
                "Stage 1B failed while retrieving documents."
            )

            raise KnowledgeBaseException(
                "Unable to retrieve documents."
            ) from error

        retrieval_time = (
            time.perf_counter()
            - retrieval_start
        )

        logger.info(
            "Hybrid retrieval completed in %.3f s.",
            retrieval_time,
        )

        # ==================================================
        # No Documents
        # ==================================================

        if not documents:
            logger.warning(
                "No relevant documents found for the question."
            )

            total_time = (
                time.perf_counter()
                - total_start
            )

            logger.info(
                "RAG request completed without a knowledge-base match."
            )

            logger.info(
                "Total Time: %.3f s.",
                total_time,
            )

            return {
                "answer": (
                    "I couldn't find any relevant information "
                    "in the uploaded documents."
                ),
                "confidence": 0.0,
                "citations": [],
                "metadata": {
                    "retrieved_documents": 0,
                    "reranker_score": 0.0,
                    "llm_model": settings.llm_model,
                    "embedding_model": settings.embedding_model,
                },
            }

        # ==================================================
        # Stage 2A: Context Formatting
        # ==================================================

        logger.info("Stage 2A: Formatting retrieved context...")

        context_start = time.perf_counter()

        context = self.format_docs(documents)

        context_time = (
            time.perf_counter()
            - context_start
        )

        logger.info(
            "Context created successfully (%d characters).",
            len(context),
        )

        logger.info(
            "Context formatting completed in %.3f s.",
            context_time,
        )

        # ==================================================
        # Stage 2B: Prompt Construction
        # ==================================================

        logger.info("Stage 2B: Creating prompt...")

        history = self.memory.get_history()

        prompt_start = time.perf_counter()

        prompt = RAG_PROMPT.invoke(
            {
                "history": history,
                "context": context,
                "question": question,
            }
        )

        prompt_time = (
            time.perf_counter()
            - prompt_start
        )

        logger.info(
            "Prompt construction completed in %.3f s.",
            prompt_time,
        )

        logger.info("=" * 70)
        logger.info("PROMPT SENT TO THE LLM")
        logger.info("=" * 70)

        prompt_text = prompt.to_string()

        if settings.log_full_prompt:
            logger.info("%s", prompt_text)
        else:
            logger.info(
                "Prompt Length: %d characters",
                len(prompt_text),
            )

        logger.info("=" * 70)

        # ==================================================
        # Stage 3: LLM Inference
        # ==================================================

        logger.info("Stage 3: Invoking LLM...")

        llm_start = time.perf_counter()

        try:
            response = self.llm.invoke(prompt)

        except Exception as error:
            logger.exception(
                "Stage 3 failed while invoking the LLM."
            )

            raise LLMException(
                "Unable to generate response."
            ) from error

        llm_time = (
            time.perf_counter()
            - llm_start
        )

        logger.info(
            "LLM inference completed in %.3f s.",
            llm_time,
        )

        # ==================================================
        # Stage 4: Response Parsing
        # ==================================================

        logger.info(
            "Stage 4: Parsing LLM response..."
        )

        parse_start = time.perf_counter()

        try:
            answer = self.output_parser.invoke(
                response
            )

        except Exception as error:
            logger.exception(
                "Stage 4 failed while parsing the LLM response."
            )

            raise LLMException(
                "Unable to process the generated response."
            ) from error

        # --------------------------------------------------
        # Conversation Memory
        # --------------------------------------------------

        self.memory.add_user_message(question)
        self.memory.add_ai_message(answer)

        parse_time = (
            time.perf_counter()
            - parse_start
        )

        logger.info(
            "Response parsing completed in %.3f s.",
            parse_time,
        )

        # ==================================================
        # Response Statistics
        # ==================================================

        answer_length = len(answer)
        word_count = len(answer.split())
        line_count = len(answer.splitlines())
        source_count = len(source_pages)
        chunk_count = len(documents)

        logger.info(
            "Answer Preview: %s",
            self.create_preview(answer),
        )

        logger.info("=" * 70)
        logger.info("RESPONSE METADATA")
        logger.info("=" * 70)

        logger.info(
            "Characters: %d",
            answer_length,
        )

        logger.info(
            "Words: %d",
            word_count,
        )

        logger.info(
            "Lines: %d",
            line_count,
        )

        logger.info(
            "Sources: %d",
            source_count,
        )

        logger.info(
            "Chunks Used: %d",
            chunk_count,
        )

        logger.info("=" * 70)

        # ==================================================
        # Citations
        # ==================================================

        citation_set = set()

        for document in documents:
            source = document.metadata.get("source")
            page = document.metadata.get("page_label")

            if source is None or page is None:
                continue

            try:
                page_number = int(page)
            except (TypeError, ValueError):
                continue

            citation_set.add(
                (
                    Path(source).name,
                    page_number,
                )
            )

        citations = [
            {
                "file": file,
                "page": page,
            }
            for file, page in sorted(citation_set)
        ]

        # ==================================================
        # Conversation History Logging
        # ==================================================

        logger.info("=" * 70)
        logger.info("Conversation History")
        logger.info("=" * 70)

        if history:
            logger.info(
                "\n%s",
                history,
            )
        else:
            logger.info(
                "No previous conversation."
            )

        # ==================================================
        # Final Performance Summary
        # ==================================================

        total_time = (
            time.perf_counter()
            - total_start
        )

        logger.info("=" * 70)
        logger.info("RAG PERFORMANCE SUMMARY")
        logger.info("=" * 70)

        logger.info(
            "Query Rewrite    : %.3f s",
            rewrite_time,
        )

        logger.info(
            "Hybrid Retrieval : %.3f s",
            retrieval_time,
        )

        logger.info(
            "Context Formatting: %.3f s",
            context_time,
        )

        logger.info(
            "Prompt Build     : %.3f s",
            prompt_time,
        )

        logger.info(
            "LLM Inference    : %.3f s",
            llm_time,
        )

        logger.info(
            "Response Parse   : %.3f s",
            parse_time,
        )

        logger.info("-" * 70)

        logger.info(
            "Total Time       : %.3f s",
            total_time,
        )

        logger.info("=" * 70)

        logger.info(
            "RAG pipeline completed successfully."
        )

        # ==================================================
        # API Response
        # ==================================================

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "metadata": {
                "retrieved_documents": len(documents),
                "retrieval_distance": round(
                    best_reranker_score,
                    4,
                ),
                "llm_model": settings.llm_model,
                "embedding_model": settings.embedding_model,
            },
        }

    # ==========================================================
    # Query Rewriting
    # ==========================================================

    def rewrite_query(
        self,
        question: str,
    ) -> str:
        """
        Rewrite a conversational question into a standalone
        retrieval query when conversation history exists.
        """

        history = self.memory.get_history()

        if not history:
            logger.info(
                "No conversation history. Query unchanged."
            )

            return question

        logger.info(
            "Conversation history detected. "
            "Running query rewriting."
        )

        prompt = QUERY_REWRITE_PROMPT.invoke(
            {
                "history": history,
                "question": question,
            }
        )

        try:
            rewritten_query = self.llm.invoke(
                prompt
            )

            rewritten_query = self.output_parser.invoke(
                rewritten_query
            )

        except Exception as error:
            logger.exception(
                "Query rewriting failed during LLM processing."
            )

            raise LLMException(
                "Unable to rewrite the query."
            ) from error

        rewritten_query = rewritten_query.strip()

        if not rewritten_query:
            logger.warning(
                "LLM returned an empty rewritten query. "
                "Using original question."
            )

            return question

        logger.info("=" * 70)
        logger.info("QUERY REWRITE")
        logger.info("Original  : %s", question)
        logger.info("Rewritten : %s", rewritten_query)
        logger.info("=" * 70)

        return rewritten_query


# ==============================================================
# Local Test
# ==============================================================

if __name__ == "__main__":

    rag = RAGService()

    while True:

        question = input(
            "\nEnter your question (or 'exit'): "
        )

        if question.lower().strip() == "exit":
            break

        response = rag.ask(question)

        print("\nAnswer:")
        print(response["answer"])