from src.core.conversation import ConversationHistory
from src.core.conversational_rag import conversational_rag
from src.core.response import RAGResponse


def test_complete_multi_turn_rag_pipeline():
    history = ConversationHistory(max_messages=10)

    queries = [
        "How many sick leave days are employees entitled to?",
        "What about the medical certificate?",
        "Is there a deadline for submitting it?",
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
        assert isinstance(result, RAGResponse)
        assert result.answer
        assert isinstance(result.sources, list)

    messages = history.get_messages()

    assert len(messages) == 6


def test_each_turn_produces_a_complete_response():
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

        assert isinstance(result.answer, str)
        assert result.answer.strip() != ""

        assert isinstance(result.sources, list)

        for source in result.sources:
            assert source.filename
            assert source.page


def test_final_history_contains_all_original_user_queries():
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

    user_messages = [
        message.content
        for message in messages
        if message.role == "user"
    ]

    assert user_messages == queries


def test_conversation_history_has_valid_user_assistant_pairs():
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

    assert len(messages) == 6

    for index in range(0, len(messages), 2):
        assert messages[index].role == "user"
        assert messages[index + 1].role == "assistant"

        assert messages[index].content
        assert messages[index + 1].content


def test_conversation_remains_usable_after_multiple_turns():
    history = ConversationHistory(max_messages=10)

    first_query = "How many sick leave days are employees entitled to?"

    conversational_rag(
        query=first_query,
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    conversational_rag(
        query="Is there a deadline for submitting it?",
        conversation_history=history,
        top_k=3,
    )

    final_query = "Can you summarize the leave requirements?"

    result = conversational_rag(
        query=final_query,
        conversation_history=history,
        top_k=3,
    )

    assert isinstance(result, RAGResponse)
    assert result.answer
    assert isinstance(result.sources, list)

    messages = history.get_messages()

    assert len(messages) == 8
    assert messages[-2].role == "user"
    assert messages[-2].content == final_query
    assert messages[-1].role == "assistant"
    assert messages[-1].content
