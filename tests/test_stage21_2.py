import src.logging_config

from src.core.conversation import (
    ConversationHistory,
    ChatMessage,
)
from src.core.conversational_rag import conversational_rag
from src.core.response import RAGResponse


def test_standalone_question_returns_rag_response():

    history = ConversationHistory(
        max_messages=10
    )

    result = conversational_rag(
        query=(
            "How many sick leave days are employees "
            "entitled to?"
        ),
        conversation_history=history,
        top_k=3,
    )

    assert isinstance(
        result,
        RAGResponse,
    )

    assert result.answer

    assert isinstance(
        result.sources,
        list,
    )


def test_follow_up_question_uses_conversation_context():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?",
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually.",
    )

    result = conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    assert isinstance(
        result,
        RAGResponse,
    )

    assert result.answer

    assert len(result.sources) >= 1


def test_original_query_is_preserved_in_history():

    history = ConversationHistory(
        max_messages=10
    )

    query = "What about the medical certificate?"

    result = conversational_rag(
        query=query,
        conversation_history=history,
        top_k=3,
    )

    messages = history.get_messages()

    assert isinstance(
        messages[-2],
        ChatMessage,
    )

    assert messages[-2].role == "user"

    assert messages[-2].content == query

    assert messages[-1].role == "assistant"

    assert messages[-1].content == result.answer


def test_multi_turn_conversation_continues():

    history = ConversationHistory(
        max_messages=10
    )

    first_query = (
        "How many sick leave days are employees entitled to?"
    )

    first_result = conversational_rag(
        query=first_query,
        conversation_history=history,
        top_k=3,
    )

    assert isinstance(
        first_result,
        RAGResponse,
    )

    second_query = (
        "What about the medical certificate?"
    )

    second_result = conversational_rag(
        query=second_query,
        conversation_history=history,
        top_k=3,
    )

    assert isinstance(
        second_result,
        RAGResponse,
    )

    assert second_result.answer

    messages = history.get_messages()

    assert len(messages) == 4

    assert messages[0].role == "user"
    assert messages[0].content == first_query

    assert messages[1].role == "assistant"
    assert messages[1].content == first_result.answer

    assert messages[2].role == "user"
    assert messages[2].content == second_query

    assert messages[3].role == "assistant"
    assert messages[3].content == second_result.answer


def test_sources_are_returned_for_follow_up():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?",
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually.",
    )

    result = conversational_rag(
        query="What about the medical certificate?",
        conversation_history=history,
        top_k=3,
    )

    assert result.sources

    for source in result.sources:

        assert source.filename

        assert source.page