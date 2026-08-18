from src.core.conversation import ConversationHistory
from src.core.conversational_rag import conversational_rag


def test_three_turn_conversation_continuity():
    history = ConversationHistory(max_messages=10)

    result_1 = conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    result_2 = conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    result_3 = conversational_rag(
        query="Is there a deadline for submitting it?",
        conversation_history=history,
        top_k=3,
    )

    assert result_1.answer
    assert result_2.answer
    assert result_3.answer

    messages = history.get_messages()

    assert len(messages) == 6

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[3].role == "assistant"
    assert messages[4].role == "user"
    assert messages[5].role == "assistant"


def test_original_queries_are_preserved_across_multiple_turns():
    history = ConversationHistory(max_messages=10)

    query_1 = "How many sick leave days are employees entitled to?"
    query_2 = "What about the medical certificate?"
    query_3 = "Is there a deadline for submitting it?"

    conversational_rag(
        query=query_1,
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query=query_2,
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query=query_3,
        conversation_history=history,
        top_k=3,
    )

    messages = history.get_messages()

    user_messages = [
        message.content
        for message in messages
        if message.role == "user"
    ]

    assert user_messages == [
        query_1,
        query_2,
        query_3,
    ]


def test_follow_up_turn_returns_sources():
    history = ConversationHistory(max_messages=10)

    conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    result = conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    assert result.answer
    assert isinstance(result.sources, list)


def test_conversation_history_contains_only_completed_turns():
    history = ConversationHistory(max_messages=10)

    conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    messages_after_turn_one = history.get_messages()

    assert len(messages_after_turn_one) == 2

    assert messages_after_turn_one[0].role == "user"
    assert messages_after_turn_one[1].role == "assistant"

    conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    messages_after_turn_two = history.get_messages()

    assert len(messages_after_turn_two) == 4


def test_history_order_is_preserved_after_three_turns():
    history = ConversationHistory(max_messages=10)

    queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there a deadline for submitting it?",
    ]

    for query in queries:
        conversational_rag(
            query=query,
            conversation_history=history,
            top_k=3,
        )

    messages = history.get_messages()

    expected_user_queries = [
        messages[0].content,
        messages[2].content,
        messages[4].content,
    ]

    assert expected_user_queries == queries
