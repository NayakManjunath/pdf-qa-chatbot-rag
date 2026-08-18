import logging

import src.logging_config

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
    """
    Generate a grounded answer using retrieved documents.

    Parameters
    ----------
    query : str
        The user's original question.

    documents : list
        Retrieved documents used as factual context.

    conversation_history : ConversationHistory, optional
        Previous conversation used to provide conversational
        context to the prompt builder.

    Returns
    -------
    RAGResponse
        Generated answer together with source references.
    """

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

    # =========================================================
    # 1. CONVERSATION HISTORY
    # =========================================================

    history_text = ""

    if conversation_history is not None:

        history_text = (
            conversation_history.format_for_prompt()
        )

        logger.info(
            "Conversation history included in prompt."
        )

    else:

        logger.info(
            "No conversation history provided."
        )

    # =========================================================
    # 2. BUILD RAG PROMPT
    # =========================================================

    prompt = build_rag_prompt(
        question=query,
        documents=documents,
        conversation_history=history_text,
    )

    logger.info(
        "RAG prompt built successfully."
    )

    # =========================================================
    # 3. LOAD LLM
    # =========================================================

    llm = get_llm()

    logger.info(
        "Sending prompt to LLM..."
    )

    response = llm.invoke(prompt)

    answer = response.content.strip()

    logger.info(
        "LLM response received."
    )

    # =========================================================
    # 4. EXTRACT SOURCES
    # =========================================================

    sources = extract_sources(
        documents
    )

    logger.info(
        "Answer generated with %d source(s).",
        len(sources),
    )

    logger.info("=" * 70)

    # =========================================================
    # 5. RETURN STRUCTURED RAG RESPONSE
    # =========================================================

    return RAGResponse(
        answer=answer,
        sources=sources,
    )


# =================================================================
# STAGE 20.4 INTEGRATION TEST
# =================================================================

if __name__ == "__main__":

    # ---------------------------------------------------------
    # Test-only imports
    # ---------------------------------------------------------

    from src.core.conversation import ConversationHistory
    from src.core.query_rewriter import rewrite_query
    from src.core.hybrid_retriever import hybrid_search

    # =========================================================
    # CREATE CONVERSATION HISTORY
    # =========================================================

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

    # =========================================================
    # CURRENT USER QUESTION
    # =========================================================

    query = "What about the medical certificate?"

    # =========================================================
    # STAGE 20.1: QUERY REWRITING
    # =========================================================

    rewrite_result = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    print()
    print("=" * 70)
    print("STAGE 20.4 - GENERATOR INTEGRATION TEST")
    print("=" * 70)

    print()
    print("Original Query:")
    print(rewrite_result.original_query)

    print()
    print("Rewritten Query:")
    print(rewrite_result.rewritten_query)

    print()
    print("Was Rewritten:")
    print(rewrite_result.was_rewritten)

    # =========================================================
    # STAGE 20.2: HYBRID RETRIEVAL
    # =========================================================

    documents = hybrid_search(
        query=rewrite_result.rewritten_query,
        top_k=3,
    )

    print()
    print(
        f"Retrieved Documents : {len(documents)}"
    )

    # =========================================================
    # DISPLAY RETRIEVED DOCUMENTS
    # =========================================================

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print()
        print(f"Rank #{index}")
        print("-" * 70)

        print(
            document.page_content[:300]
        )

        print()

        print(
            f"Source : "
            f"{document.metadata.get('filename', 'unknown')}"
        )

        print(
            f"Page : "
            f"{document.metadata.get('page_label', 'unknown')}"
        )

    # =========================================================
    # STAGE 20.4: GENERATE FINAL ANSWER
    # =========================================================

    result = generate_answer(
        query=query,
        documents=documents,
        conversation_history=history,
    )

    # =========================================================
    # DISPLAY FINAL ANSWER
    # =========================================================

    print()
    print("=" * 70)
    print("FINAL RAG ANSWER")
    print("=" * 70)

    print()
    print(result.answer)

    # =========================================================
    # DISPLAY SOURCES
    # =========================================================

    print()
    print("=" * 70)
    print("SOURCES")
    print("=" * 70)

    for index, source in enumerate(
        result.sources,
        start=1,
    ):

        print(
            f"{index}. "
            f"{source.filename}, "
            f"Page {source.page}"
        )

    print()
    print("=" * 70)
    print("STAGE 20.4 TEST COMPLETED")
    print("=" * 70)
