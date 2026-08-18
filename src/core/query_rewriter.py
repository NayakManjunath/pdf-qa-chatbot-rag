import logging
from dataclasses import dataclass

import src.logging_config

from src.core.llm import get_llm


logger = logging.getLogger(__name__)


MAX_REWRITTEN_QUERY_LENGTH = 300


@dataclass
class QueryRewriteResult:
    original_query: str
    rewritten_query: str
    was_rewritten: bool


def _clean_rewritten_query(query: str) -> str:
    """
    Clean the raw LLM output before using it for retrieval.
    """

    query = query.strip()

    # Remove surrounding quotes if the LLM added them.
    query = query.strip('"').strip("'").strip()

    return query


def rewrite_query(
    query: str,
    conversation_history: str = "",
) -> QueryRewriteResult:
    """
    Convert a conversational question into a standalone
    retrieval query.

    If there is no conversation history, the original query
    is returned unchanged.
    """

    original_query = query.strip()

    logger.info("=" * 70)
    logger.info("QUERY UNDERSTANDING / REWRITING")
    logger.info("=" * 70)

    logger.info(
        "Original Query: %s",
        original_query,
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    if not original_query:
        logger.warning(
            "Empty query received."
        )

        return QueryRewriteResult(
            original_query="",
            rewritten_query="",
            was_rewritten=False,
        )

    # ---------------------------------------------------------
    # No conversation history
    # ---------------------------------------------------------

    if not conversation_history.strip():

        logger.info(
            "No conversation history. Query unchanged."
        )

        return QueryRewriteResult(
            original_query=original_query,
            rewritten_query=original_query,
            was_rewritten=False,
        )

    # ---------------------------------------------------------
    # Query rewriting prompt
    # ---------------------------------------------------------

    prompt = f"""
You are a query rewriting component for a document
retrieval system.

Your ONLY task is to convert the CURRENT USER QUESTION
into a short, standalone search query.

You are NOT answering the question.

==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
CURRENT USER QUESTION
==================================================

{original_query}

==================================================
RULES
==================================================

1. Use conversation history only when necessary to
   understand the current question.

2. Resolve conversational references such as:

   - it
   - this
   - that
   - they
   - them
   - it
   - what about
   - how about
   - what approval
   - when should I

3. Preserve the original meaning.

4. Preserve the main topic when the current question
   depends on previous conversation.

5. If the current question is already standalone,
   keep it substantially unchanged.

6. Do NOT answer the question.

7. Do NOT invent facts.

8. Do NOT introduce names, numbers, dates, policies,
   entities, or details that are not present in the
   conversation.

9. Do NOT mention the conversation history.

10. Do NOT provide explanations.

11. Do NOT output labels.

12. Return ONLY the final standalone search query.

13. Keep the output short and suitable for:

    - vector search
    - BM25 retrieval
    - semantic retrieval

==================================================
EXAMPLES
==================================================

Conversation:
USER: How many sick leave days are employees entitled to?
ASSISTANT: Employees are entitled to 10 paid sick leave days annually.

Current question:
What about the medical certificate?

Output:
medical certificate requirement for sick leave


Conversation:
USER: How many annual leave days do employees receive?
ASSISTANT: Employees receive 24 annual leave days per calendar year.

Current question:
How do I request it?

Output:
how to request annual leave


Conversation:
USER: Can employees work remotely?
ASSISTANT: Employees may work remotely with manager approval.

Current question:
What approval is needed?

Output:
manager approval for remote work


Conversation:
USER: What does the attendance policy say?
ASSISTANT: Unplanned absences should be reported to the reporting manager before the start of the workday.

Current question:
When should I report it?

Output:
when to report unplanned absence


Conversation:
USER: How many sick leave days are employees entitled to?
ASSISTANT: Employees are entitled to 10 paid sick leave days annually.

Current question:
What are the company's working hours?

Output:
company working hours

==================================================
FINAL OUTPUT
==================================================

Return ONLY the standalone search query.
"""

    # ---------------------------------------------------------
    # LLM
    # ---------------------------------------------------------

    llm = get_llm()

    logger.info(
        "Sending query rewriting prompt to LLM..."
    )

    response = llm.invoke(prompt)

    rewritten_query = _clean_rewritten_query(
        response.content
    )

    # ---------------------------------------------------------
    # Validate LLM output
    # ---------------------------------------------------------

    if not rewritten_query:

        logger.warning(
            "LLM returned an empty rewritten query. "
            "Falling back to original query."
        )

        rewritten_query = original_query

    if len(rewritten_query) > MAX_REWRITTEN_QUERY_LENGTH:

        logger.warning(
            "Rewritten query exceeds maximum length. "
            "Falling back to original query."
        )

        rewritten_query = original_query

    # ---------------------------------------------------------
    # Determine whether rewriting occurred
    # ---------------------------------------------------------

    was_rewritten = (
        rewritten_query.lower()
        != original_query.lower()
    )

    logger.info(
        "Rewritten Query: %s",
        rewritten_query,
    )

    logger.info(
        "Was Rewritten: %s",
        was_rewritten,
    )

    logger.info("=" * 70)

    return QueryRewriteResult(
        original_query=original_query,
        rewritten_query=rewritten_query,
        was_rewritten=was_rewritten,
    )

if __name__ == "__main__":

    history = """
USER: How many sick leave days are employees entitled to?
ASSISTANT: Employees are entitled to 10 paid sick leave days annually.
"""

    query = "What about the medical certificate?"

    result = rewrite_query(
        query=query,
        conversation_history=history,
    )

    print()
    print("=" * 70)
    print("STAGE 20 - QUERY REWRITING TEST")
    print("=" * 70)

    print()
    print("Original Query:")
    print(result.original_query)

    print()
    print("Rewritten Query:")
    print(result.rewritten_query)

    print()
    print("Was Rewritten:")
    print(result.was_rewritten)

    print("=" * 70)
