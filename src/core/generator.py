import logging

import src.logging_config

from src.core.query_rewriter import rewrite_query
from src.core.conversation import ConversationHistory

from src.core.llm import get_llm
from src.core.prompt_builder import build_rag_prompt
from src.core.response import (
    RAGResponse,
    extract_sources,
)

logger = logging.getLogger(__name__)




def generate_answer(
    query: str,
    documents,
    conversation_history=None,
) -> RAGResponse:

    logger.info("=" * 70)
    logger.info("RAG ANSWER GENERATION")
    logger.info("=" * 70)

    logger.info(
        "Question : %s",
        query,
    )

    logger.info(
        "Context Documents : %d",
        len(documents),
    )

    # ---------------------------------------------------------
    # CONVERSATION HISTORY
    # ---------------------------------------------------------

    history_text = ""

    if conversation_history is not None:

        history_text = (
            conversation_history.format_for_prompt()
        )

    # ---------------------------------------------------------
    # BUILD RAG PROMPT
    # ---------------------------------------------------------

    prompt = build_rag_prompt(
        question=query,
        documents=documents,
        conversation_history=history_text,
    )

    # ---------------------------------------------------------
    # LOAD LLM
    # ---------------------------------------------------------

    llm = get_llm()

    logger.info(
        "Sending prompt to LLM..."
    )

    response = llm.invoke(prompt)

    answer = response.content

    logger.info(
        "LLM response received."
    )

    # ---------------------------------------------------------
    # EXTRACT SOURCES
    # ---------------------------------------------------------

    sources = extract_sources(
        documents
    )

    logger.info(
        "Answer generated with %d source(s).",
        len(sources),
    )

    logger.info("=" * 70)

    return RAGResponse(
        answer=answer,
        sources=sources,
    )


if __name__ == "__main__":

    from src.core.hybrid_retriever import hybrid_search

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    query = "What about the medical certificate?"

    rewritten_query = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    print()
    print("=" * 70)
    print("CONVERSATION-AWARE RETRIEVAL")
    print("=" * 70)

    print(
        f"Original Query : {query}"
    )

    print(
        f"Rewritten Query : {rewritten_query}"
    )

    documents = hybrid_search(
        query=rewritten_query,
        top_k=3,
    )

    print()
    print(
        f"Retrieved Documents : {len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print()
        print(
            f"Rank #{index}"
        )

        print(
            document.page_content[:300]
        )

        print(
            f"Source : "
            f"{document.metadata.get('source')}"
        )

        print(
            f"Page : "
            f"{document.metadata.get('page', 0) + 1}"
        )

    print("=" * 70)

# def generate_answer(
#     query: str,
#     documents,
#     conversation_history: ConversationHistory | None = None,
# ) -> RAGResponse:
#     """
#     Generate a grounded answer using retrieved documents
#     and optional conversation history.

#     The conversation history is used only to understand
#     the context of the current question.
#     """

#     logger.info("=" * 70)
#     logger.info("RAG ANSWER GENERATION")
#     logger.info("=" * 70)

#     logger.info(
#         "Question : %s",
#         query,
#     )

#     logger.info(
#         "Context Documents : %d",
#         len(documents),
#     )

#     # --------------------------------------------------
#     # Conversation History
#     # --------------------------------------------------

#     if conversation_history is None:
#         conversation_history = ConversationHistory()

#     history_text = conversation_history.format_for_prompt()

#     logger.info(
#         "Conversation History Messages : %d",
#         len(conversation_history.messages),
#     )

#     rewritten_query = query

#     if conversation_history is not None:
#         rewritten_query = rewrite_query(
#             query=query,
#             conversation_history=conversation_history.format_for_prompt(),
#         )

#         logger.info(
#         "Original Query : %s",
#         query,
#     )

#     logger.info(
#         "Retrieval Query : %s",
#         rewritten_query,
#     )
#     # --------------------------------------------------
#     # Build RAG Prompt
#     # --------------------------------------------------

#     prompt = build_rag_prompt(
#         question=query,
#         documents=documents,
#         conversation_history=history_text,
#     )

#     logger.info(
#         "RAG prompt built successfully."
#     )

#     # --------------------------------------------------
#     # Load LLM
#     # --------------------------------------------------

#     llm = get_llm()

#     logger.info(
#         "Sending prompt to LLM..."
#     )

#     response = llm.invoke(prompt)

#     answer = response.content

#     logger.info(
#         "LLM response received."
#     )

#     # --------------------------------------------------
#     # Extract Sources
#     # --------------------------------------------------

#     sources = extract_sources(
#         documents
#     )

#     logger.info(
#         "Answer generated with %d source(s).",
#         len(sources),
#     )

#     # --------------------------------------------------
#     # Update Conversation History
#     # --------------------------------------------------

#     conversation_history.add_message(
#     "user",
#     query,
#     )

#     conversation_history.add_message(
#         "assistant",
#         answer,
#     )

#     logger.info(
#         "Conversation history updated."
#     )

#     logger.info("=" * 70)

#     return RAGResponse(
#         answer=answer,
#         sources=sources,
#     )

# def generate_answer(
#     query: str,
#     documents,
#     conversation_history=None,
# ) -> RAGResponse:

#     logger.info("=" * 70)
#     logger.info("RAG ANSWER GENERATION")
#     logger.info("=" * 70)

#     logger.info(
#         "Question : %s",
#         query,
#     )

#     logger.info(
#         "Context Documents : %d",
#         len(documents),
#     )

#     history_text = ""

#     if conversation_history is not None:
#         history_text = (
#             conversation_history.format_for_prompt()
#         )

#     prompt = build_rag_prompt(
#         question=query,
#         documents=documents,
#         conversation_history=history_text,
#     )

#     llm = get_llm()

#     logger.info(
#         "Sending prompt to LLM..."
#     )

#     response = llm.invoke(prompt)

#     answer = response.content

#     logger.info(
#         "LLM response received."
#     )

#     sources = extract_sources(
#         documents
#     )

#     logger.info(
#         "Answer generated with %d source(s).",
#         len(sources),
#     )

#     logger.info("=" * 70)

#     return RAGResponse(
#         answer=answer,
#         sources=sources,
#     )