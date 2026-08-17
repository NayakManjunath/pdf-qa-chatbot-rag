import logging 

import src.logging_config

from src.core.conversation import ConversationHistory
from src.core.query_rewriter import rewrite_query
from src.core.hybrid_retriever import hybrid_search
from src.core.generator import generate_answer
from src.core.response import RAGResponse

logger = logging.getLogger(__name__)

def conversational_rag(

        query: str,
        conversation_history : ConversationHistory,
        top_k : int = 3,
)-> RAGResponse:

    logger.info("=" * 70)
    logger.info("CONVERSATIONAL RAG")
    logger.info("=" * 70)
    logger.info(
        "User Query: %s",
        query,
    )

    # Step 1: Query Rewriting
    logger.info(
        "Conversation History Type : %s",
        type(conversation_history),
    )

    history_text = conversation_history.format_for_prompt()

    rewritten_query = rewrite_query(

        query = query,
        conversation_history= history_text,
    )

    logger.info(
        "Rewrite Query: %s",
        rewritten_query,
    )

    # step 2 : Hybrid Retrieval

    documents = hybrid_search(

        query = rewritten_query,
        top_k= top_k
    )

    logger.info(
        "Retrievl documents : %d",
        len(documents),
    )

    # step 3: Generate answer

    result = generate_answer(
        query=query,
        documents=documents,
        conversation_history=conversation_history,
    )

    #step 4 : Update conversation History 

    conversation_history.add_message(

        "user",
        query,

        
    )
    conversation_history.add_message(

        "assistant",
        result.answer

    )
    logger.info(
        "Conversation history updated"
    )
    logger.info("=" * 70)

    return result

if __name__ == "__main__":

    history = ConversationHistory(
        max_messages=10
    )

    print()
    print("=" * 70)
    print("STAGE 19.4")
    print("END-TO-END CONVERSATIONAL RAG TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # TURN 1
    # ---------------------------------------------------------

    query_1 = (
        "How many sick leave days are employees entitled to?"
    )

    result_1 = conversational_rag(
        query=query_1,
        conversation_history=history,
        top_k=3,
    )

    print()
    print("TURN 1")
    print("-" * 70)

    print(
        f"USER: {query_1}"
    )

    print(
        f"ASSISTANT: {result_1.answer}"
    )

    print()
    print("SOURCES")

    for index, source in enumerate(
        result_1.sources,
        start=1,
    ):

        print(
            f"{index}. "
            f"{source.filename}, "
            f"Page {source.page}"
        )

    # ---------------------------------------------------------
    # TURN 2
    # ---------------------------------------------------------

    query_2 = (
        "What about the medical certificate?"
    )

    result_2 = conversational_rag(
        query=query_2,
        conversation_history=history,
        top_k=3,
    )

    print()
    print("TURN 2")
    print("-" * 70)

    print(
        f"USER: {query_2}"
    )

    print(
        f"ASSISTANT: {result_2.answer}"
    )

    print()
    print("SOURCES")

    for index, source in enumerate(
        result_2.sources,
        start=1,
    ):

        print(
            f"{index}. "
            f"{source.filename}, "
            f"Page {source.page}"
        )

    print()
    print("=" * 70)

    print("FINAL CONVERSATION HISTORY")
    print("=" * 70)

    print(
        history.format_for_prompt()
    )

    print("=" * 70)