from src.core.conversation import ConversationHistory
from src.core.conversational_rag import conversational_rag


def test_follow_up_retrieval_uses_conversation_context():
    history = ConversationHistory(max_messages=10)

    first_query = "How many sick leave days are employees entitled to?"

    conversational_rag(
        query=first_query,
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


def test_new_topic_remains_independent_from_previous_topic():
    history = ConversationHistory(max_messages=10)

    conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    result = conversational_rag(
        query="What is the employee retirement policy?",
        conversation_history=history,
        top_k=3,
    )

    assert result.answer
    assert isinstance(result.sources, list)


def test_follow_up_preserves_original_user_question():
    history = ConversationHistory(max_messages=10)

    first_query = "How many sick leave days are employees entitled to?"
    second_query = "What about the medical certificate?"

    conversational_rag(
        query=first_query,
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query=second_query,
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
        first_query,
        second_query,
    ]


def test_retrieval_context_does_not_change_conversation_history():
    history = ConversationHistory(max_messages=10)

    first_query = "How many sick leave days are employees entitled to?"

    conversational_rag(
        query=first_query,
        conversation_history=history,
        top_k=3,
    )

    before_follow_up = history.get_messages()

    conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    after_follow_up = history.get_messages()

    assert len(before_follow_up) == 2
    assert len(after_follow_up) == 4

    assert after_follow_up[0].content == first_query


def test_multi_turn_retrieval_keeps_conversation_order():
    history = ConversationHistory(max_messages=10)

    queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there a deadline for submitting it?",
    ]

    for query in queries:
        result = conversational_rag(
            query=query,
            conversation_history=history,
            top_k=3,
        )

        assert result.answer
        assert isinstance(result.sources, list)

    messages = history.get_messages()

    assert len(messages) == 6

    for index, query in enumerate(queries):
        assert messages[index * 2].role == "user"
        assert messages[index * 2].content == query
        assert messages[index * 2 + 1].role == "assistant"
