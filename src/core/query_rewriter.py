import logging 
import src.logging_config

from src.core.llm import get_llm

logger = logging.getLogger(__name__)

def rewrite_query(
    query: str,
    conversation_history: str = "",
) -> str:

    logger.info("=" * 70)
    logger.info("QUERY REWRITING")
    logger.info("=" * 70)

    logger.info(
        "Original Query: %s",
        query,
    )

    if not conversation_history.strip():

        logger.info(
            "No conversation history. Query unchanged."
        )

        return query.strip()

#     prompt = f"""
# You are a query rewriting component for a
# document question-answering system.

# Your ONLY task is to create a standalone search
# query for document retrieval.

# Current User Question:
# {query}

# Conversation History:
# {conversation_history}

# Rules:

# 1. If the current question is already standalone,
#    return it unchanged.

# 2. If the current question depends on previous
#    conversation, resolve the references using the
#    conversation history.

# 3. Preserve important subject context from the
#    conversation when it is necessary for retrieval.

# 4. Do not answer the question.

# 5. Do not introduce facts that are not present
#    in the conversation.

# 6. Do not invent entities, policies, numbers,
#    dates, names, or other information.

# 7. Do not include explanations.

# 8. Return ONLY the standalone search query.

# Examples:

# Conversation:
# USER: How many sick leave days are employees entitled to?
# ASSISTANT: Employees are entitled to 10 paid sick leave days annually.

# Current Question:
# What about the medical certificate?

# Good rewritten query:
# medical certificate requirement for sick leave

# ---

# Conversation:
# USER: What are the working hours?
# ASSISTANT: Standard working hours are Monday to Friday, 9:00 AM to 6:00 PM.

# Current Question:
# What about the medical certificate?

# Good rewritten query:
# medical certificate requirement

# ---

# If no rewriting is necessary, return the
# current question as-is.

# Standalone Search Query:
# """

    prompt = f"""
    You are a query rewriting component for a document
    retrieval system.

    Your task is ONLY to rewrite the CURRENT USER QUESTION
    into a standalone search query.

    You are NOT answering the question.

    ==================================================
    CONVERSATION HISTORY
    ==================================================

    {conversation_history}

    ==================================================
    CURRENT USER QUESTION
    ==================================================

    {query}

    ==================================================
    RULES
    ==================================================

    1. Use the conversation history to understand references
    in the current question.

    2. Resolve words such as:
    - it
    - this
    - that
    - they
    - them
    - what about
    - how about
    - what approval
    - when should I

    3. Preserve the main topic from the conversation when
    the current question depends on it.

    4. If the current question is already standalone,
    you may simplify it, but preserve its meaning.

    5. Do NOT answer the question.

    6. Do NOT invent facts.

    7. Do NOT introduce names, numbers, dates, policies,
    entities, or details that are not present in the
    conversation.

    8. Do NOT mention the conversation history.

    9. Do NOT output explanations.

    10. Do NOT output labels such as:
        "Current User Question:"
        "Conversation History:"
        "Standalone Search Query:"

    11. Return ONLY the final search query.

    12. The final output must be a short standalone
        search query suitable for vector search and BM25.

    ==================================================
    EXAMPLES
    ==================================================

    Example 1:

    Conversation:
    User: How many sick leave days are employees entitled to?
    Assistant: Employees are entitled to 10 paid sick leave days annually.

    Current question:
    What about the medical certificate?

    Output:
    medical certificate requirement for sick leave


    Example 2:

    Conversation:
    User: How many annual leave days do employees receive?
    Assistant: Employees receive 24 annual leave days per calendar year.

    Current question:
    How do I request it?

    Output:
    how to request annual leave


    Example 3:

    Conversation:
    User: Can employees work remotely?
    Assistant: Employees may work remotely up to two days per week with manager approval.

    Current question:
    What approval is needed?

    Output:
    manager approval for remote work


    Example 4:

    Conversation:
    User: What does the attendance policy say?
    Assistant: Unplanned absences should be reported to the reporting manager before the start of the workday.

    Current question:
    When should I report it?

    Output:
    when to report unplanned absence


    Example 5:

    Conversation:
    User: How many sick leave days are employees entitled to?
    Assistant: Employees are entitled to 10 paid sick leave days annually.

    Current question:
    What are the company's working hours?

    Output:
    company working hours

    ==================================================
    FINAL OUTPUT
    ==================================================

    Return ONLY the standalone search query.
    """



    llm = get_llm()

    logger.info(
        "Sending query rewriting prompt to LLM..."
    )

    response = llm.invoke(prompt)

    rewritten_query = response.content.strip()
    rewritten_query = rewritten_query.strip().strip('"').strip("'")

    logger.info(
        "Rewritten Query : %s",
        rewritten_query,
    )

    logger.info("=" * 70)

    return rewritten_query

if __name__ == "__main__":

    # history = """

    # User: How many sick leave days are employees entitled to?

    # Assistant: Employees are entitled to 10 paid sick leave days annually.

    # """

    # query = "What about the medical certificate?"

    # history = """

    # User: How many sick leave days are employees entitled to?

    # Assistant: Employees are entitled to 10 paid sick leave days annually.

    # """

    # query = "What are the company's working hours?"

    # history = """

    # User: How many annual leave days do employees receive?

    # Assistant: Employees receive 24 annual leave days per calendar year.

    # """

    # query = "How do I request it?"

    # history = """

    # User: Can employees work remotely?

    # Assistant: Employees may work remotely up to two days per week with manager approval.

    # """

    # query = "What approval is needed?"

    # history = """

    # User: What does the attendance policy say?

    # Assistant: Employees are expected to maintain regular attendance. Unplanned absences should be reported to the reporting manager before the start of the workday.

    # """

    # query = "When should I report it?"
    history = """

        User: What does the attendance policy say?

        Assistant: Employees are expected to maintain regular attendance. Unplanned absences should be reported to the reporting manager before the start of the workday.

        """

    query = "When should I report it?"


    rewritten = rewrite_query(
        query=query,
        conversation_history=history,
    )

    print()
    print("=" * 70)
    print("QUERY REWRITE TEST")
    print("=" * 70)

    print("Original Query:")
    print(query)

    print()

    print("Conversation History:")
    print(history)

    print()

    print("Rewritten Query:")
    print(rewritten)

    print("=" * 70)