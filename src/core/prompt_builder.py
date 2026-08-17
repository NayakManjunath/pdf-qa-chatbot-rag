import logging

import src.logging_config

logger = logging.getLogger(__name__)


def build_rag_prompt(
    question: str,
    documents: list,
    conversation_history: str = "",
) -> str:
    """
    Build a grounded RAG prompt using:
    1. Conversation history for conversational context
    2. Retrieved documents as the only factual source
    3. The user's current question
    """

    logger.info("=" * 70)
    logger.info("Building RAG Prompt")
    logger.info("=" * 70)

    logger.info(
        "Question : %s",
        question,
    )

    logger.info(
        "Content Documents : %d",
        len(documents),
    )

    # ============================================================
    # Conversation History
    # ============================================================

    history_section = ""

    if conversation_history.strip():

        history_section = f"""
Conversation History:
{conversation_history}

Use the conversation history only to understand
the context of the user's current question.

Do not treat conversation history as a source of
factual information.

Answers must still be based only on the
provided documents.
"""

    # ============================================================
    # Build Retrieved Context
    # ============================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        source = document.metadata.get(
            "filename",
            "unknown",
        )

        page = document.metadata.get(
            "page_label",
            document.metadata.get(
                "page",
                "unknown",
            ),
        )

        context_parts.append(
            f"""
--- Document {index} ---
Source: {source}
Page: {page}

{document.page_content}
"""
        )

    context = "\n".join(context_parts)

    # ============================================================
    # Build Final RAG Prompt
    # ============================================================

    prompt = f"""
You are a helpful document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context, say:

"I could not find the answer in the provided documents."

Do not use outside knowledge.
Do not invent or assume information.

{history_section}

Context:
{context}

User Question:
{question}

Answer:
"""

    logger.info(
        "RAG prompt built successfully."
    )

    return prompt


# ================================================================
# TEST
# ================================================================

if __name__ == "__main__":

    from src.core.hybrid_retriever import hybrid_search

    # Current conversational question
    query = "What about the medical certificate?"

    # ------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------

    conversation_history = """
USER: How many sick leave days are employees entitled to?
ASSISTANT: Employees are entitled to 10 paid sick leave days annually.
"""

    # ------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------
    #
    # For this test, we use the original topic as the retrieval
    # query because "medical certificate" is a follow-up question.
    #
    # Later, Stage 19.x will make this query rewriting automatic.
    # ------------------------------------------------------------

    retrieval_query = (
        "How many sick leave days are employees entitled to?"
    )

    documents = hybrid_search(
        query=retrieval_query,
        top_k=3,
    )

    # ------------------------------------------------------------
    # Build conversational RAG prompt
    # ------------------------------------------------------------

    prompt = build_rag_prompt(
        question=query,
        documents=documents,
        conversation_history=conversation_history,
    )

    # ------------------------------------------------------------
    # Display
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("GENERATED RAG PROMPT")
    print("=" * 70)
    print(prompt)
    print("=" * 70)

