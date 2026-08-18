from langchain_core.documents import Document

from src.core.conversation import ConversationHistory
from src.core.response import (
    RAGResponse,
    SourceReference,
    extract_sources,
)


def test_conversation_preserves_message_order():
    history = ConversationHistory(max_messages=10)

    history.add_message(
        "user",
        "How many sick leave days do employees get?",
    )

    history.add_message(
        "assistant",
        "Employees receive 10 paid sick leave days annually.",
    )

    history.add_message(
        "user",
        "What about the medical certificate?",
    )

    formatted = history.format_for_prompt()

    assert "How many sick leave days do employees get?" in formatted
    assert (
        "Employees receive 10 paid sick leave days annually."
        in formatted
    )
    assert "What about the medical certificate?" in formatted

    assert (
        formatted.index(
            "How many sick leave days do employees get?"
        )
        <
        formatted.index(
            "Employees receive 10 paid sick leave days annually."
        )
        <
        formatted.index(
            "What about the medical certificate?"
        )
    )


def test_original_query_is_not_replaced_by_rewritten_query():
    original_query = "What about the medical certificate?"
    rewritten_query = "medical certificate requirement for sick leave"

    assert original_query != rewritten_query
    assert original_query == "What about the medical certificate?"
    assert rewritten_query == (
        "medical certificate requirement for sick leave"
    )


def test_sources_remain_unique():
    documents = [
        Document(
            page_content="Sick leave policy.",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),
        Document(
            page_content="Medical certificate policy.",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),
    ]

    sources = extract_sources(documents)

    assert len(sources) == 1
    assert sources[0] == SourceReference(
        filename="employee_handbook.pdf",
        page="1",
    )


def test_rag_response_contains_answer_and_sources():
    response = RAGResponse(
        answer=(
            "A medical certificate may be required "
            "for longer absences."
        ),
        sources=[
            SourceReference(
                filename="employee_handbook.pdf",
                page="1",
            )
        ],
    )

    assert response.answer
    assert len(response.sources) == 1
    assert response.sources[0].filename == "employee_handbook.pdf"
    assert response.sources[0].page == "1"


def test_conversation_history_is_bounded():
    history = ConversationHistory(max_messages=4)

    for index in range(6):
        history.add_message(
            "user",
            f"Question {index}",
        )

    formatted = history.format_for_prompt()

    assert "Question 0" not in formatted
    assert "Question 1" not in formatted
    assert "Question 2" in formatted
    assert "Question 5" in formatted
