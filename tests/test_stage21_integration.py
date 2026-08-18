from src.core.conversation import ConversationHistory
from src.core.conversational_rag import conversational_rag


def test_complete_single_turn_rag_flow():

    history = ConversationHistory(
        max_messages=10
    )

    result = conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    assert result is not None
    assert result.answer
    assert result.sources

    messages = history.get_messages()

    assert len(messages) == 2

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_follow_up_uses_previous_conversation():

    history = ConversationHistory(
        max_messages=10
    )

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

    assert result is not None
    assert result.answer
    assert result.sources

    messages = history.get_messages()

    assert len(messages) == 4

    assert messages[2].role == "user"
    assert messages[2].content == "What about the medical certificate?"

    assert messages[3].role == "assistant"


def test_three_turn_conversation_remains_coherent():

    history = ConversationHistory(
        max_messages=10
    )

    queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there any documentation requirement?",
    ]

    results = []

    for query in queries:

        result = conversational_rag(
            query=query,
            conversation_history=history,
            top_k=3,
        )

        results.append(result)

    assert len(results) == 3

    for result in results:

        assert result is not None
        assert result.answer
        assert result.sources

    messages = history.get_messages()

    assert len(messages) == 6


def test_original_queries_remain_unchanged():

    history = ConversationHistory(
        max_messages=10
    )

    original_queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there any documentation requirement?",
    ]

    for query in original_queries:

        conversational_rag(
            query=query,
            conversation_history=history,
            top_k=3,
        )

    messages = history.get_messages()

    stored_user_queries = [
        message.content
        for message in messages
        if message.role == "user"
    ]

    assert stored_user_queries == original_queries


def test_assistant_responses_are_stored_after_each_turn():

    history = ConversationHistory(
        max_messages=10
    )

    conversational_rag(
        query="How many sick leave days are employees entitled to?",
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    messages = history.get_messages()

    assert len(messages) == 4

    for index in range(0, len(messages), 2):

        assert messages[index].role == "user"
        assert messages[index + 1].role == "assistant"

        assert messages[index].content
        assert messages[index + 1].content


def test_retrieval_does_not_corrupt_conversation_state():

    history = ConversationHistory(
        max_messages=10
    )

    first_query = (
        "How many sick leave days are employees entitled to?"
    )

    second_query = (
        "What about the medical certificate?"
    )

    conversational_rag(
        query=first_query,
        conversation_history=history,
        top_k=3,
    )

    before_second_turn = history.get_messages()

    conversational_rag(
        query=second_query,
        conversation_history=history,
        top_k=3,
    )

    after_second_turn = history.get_messages()

    assert len(before_second_turn) == 2
    assert len(after_second_turn) == 4

    assert after_second_turn[0].content == first_query
    assert after_second_turn[2].content == second_query


def test_separate_conversations_remain_isolated():

    history_a = ConversationHistory(
        max_messages=10
    )

    history_b = ConversationHistory(
        max_messages=10
    )

    query_a = (
        "How many sick leave days are employees entitled to?"
    )

    query_b = (
        "What is the employee attendance policy?"
    )

    conversational_rag(
        query=query_a,
        conversation_history=history_a,
        top_k=3,
    )

    conversational_rag(
        query=query_b,
        conversation_history=history_b,
        top_k=3,
    )

    messages_a = history_a.get_messages()
    messages_b = history_b.get_messages()

    assert len(messages_a) == 2
    assert len(messages_b) == 2

    assert messages_a[0].content == query_a
    assert messages_b[0].content == query_b

    assert messages_a[0].content != messages_b[0].content


def test_conversation_remains_usable_after_multiple_turns():

    history = ConversationHistory(
        max_messages=10
    )

    queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there any documentation requirement?",
        "Who approves the leave?",
    ]

    for query in queries:

        result = conversational_rag(
            query=query,
            conversation_history=history,
            top_k=3,
        )

        assert result.answer
        assert result.sources

    messages = history.get_messages()

    assert len(messages) == 8

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"

    assert messages[-2].role == "user"
    assert messages[-1].role == "assistant"