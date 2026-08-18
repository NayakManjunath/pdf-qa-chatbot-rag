import logging

import src.logging_config

from langchain_core.documents import Document

from src.core.conversation import ConversationHistory
from src.core.query_rewriter import (
    rewrite_query,
    QueryRewriteResult,
)
from src.core.response import (
    extract_sources,
    RAGResponse,
    SourceReference,
)


logger = logging.getLogger(__name__)


# ======================================================================
# STAGE 20.5
# DEDICATED TEST CASES
# ======================================================================


def test_query_rewrite_result_structure():
    """
    Verify that query rewriting returns the expected
    QueryRewriteResult structure.
    """

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    result = rewrite_query(
        query="What about the medical certificate?",
        conversation_history=history.format_for_prompt(),
    )

    assert isinstance(
        result,
        QueryRewriteResult,
    )

    assert result.original_query == (
        "What about the medical certificate?"
    )

    assert isinstance(
        result.rewritten_query,
        str,
    )

    assert isinstance(
        result.was_rewritten,
        bool,
    )


# ======================================================================
# TEST 2
# EMPTY QUERY
# ======================================================================


def test_empty_query():

    result = rewrite_query(
        query="",
        conversation_history="",
    )

    assert isinstance(
        result,
        QueryRewriteResult,
    )

    assert result.original_query == ""

    assert result.rewritten_query == ""

    assert result.was_rewritten is False


# ======================================================================
# TEST 3
# STANDALONE QUERY
# ======================================================================


def test_standalone_query():

    query = "What are the company's working hours?"

    result = rewrite_query(
        query=query,
        conversation_history="",
    )

    assert result.original_query == query

    assert result.rewritten_query == query

    assert result.was_rewritten is False


# ======================================================================
# TEST 4
# CONVERSATIONAL FOLLOW-UP
# ======================================================================


def test_conversational_follow_up():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    result = rewrite_query(
        query="What about the medical certificate?",
        conversation_history=history.format_for_prompt(),
    )

    assert result.was_rewritten is True

    assert result.rewritten_query

    rewritten = result.rewritten_query.lower()

    assert "medical" in rewritten

    assert "certificate" in rewritten


# ======================================================================
# TEST 5
# NEW TOPIC AFTER CONVERSATION
# ======================================================================


def test_new_topic_after_conversation():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    query = "What are the company's working hours?"

    result = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    rewritten = result.rewritten_query.lower()

    assert "working" in rewritten

    assert "hours" in rewritten

    assert "sick" not in rewritten


# ======================================================================
# TEST 6
# SOURCE EXTRACTION
# ======================================================================


def test_source_extraction_returns_unique_sources():

    documents = [

        Document(
            page_content="Employees receive sick leave.",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),

        Document(
            page_content="Medical certificate may be required.",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),

        Document(
            page_content="Maternity leave policy.",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "2",
            },
        ),

    ]

    sources = extract_sources(
        documents
    )

    assert isinstance(
        sources,
        list,
    )

    assert len(sources) == 2

    assert SourceReference(
        filename="employee_handbook.pdf",
        page="1",
    ) in sources

    assert SourceReference(
        filename="employee_handbook.pdf",
        page="2",
    ) in sources


# ======================================================================
# TEST 7
# RAG RESPONSE STRUCTURE
# ======================================================================


def test_rag_response_structure():

    sources = [
        SourceReference(
            filename="employee_handbook.pdf",
            page="1",
        )
    ]

    response = RAGResponse(
        answer=(
            "A medical certificate may be required "
            "for absences longer than two consecutive days."
        ),
        sources=sources,
    )

    assert isinstance(
        response,
        RAGResponse,
    )

    assert isinstance(
        response.answer,
        str,
    )

    assert response.answer

    assert isinstance(
        response.sources,
        list,
    )

    assert len(response.sources) == 1


# ======================================================================
# TEST 8
# CONVERSATION HISTORY
# ======================================================================


def test_conversation_history():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    formatted_history = (
        history.format_for_prompt()
    )

    assert isinstance(
        formatted_history,
        str,
    )

    assert "sick leave" in formatted_history.lower()

    assert "10" in formatted_history


# ======================================================================
# TEST 9
# MULTI-TURN CONVERSATION HISTORY
# ======================================================================


def test_multi_turn_conversation_history():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "How many sick leave days are employees entitled to?"
    )

    history.add_message(
        "assistant",
        "Employees are entitled to 10 paid sick leave days annually."
    )

    history.add_message(
        "user",
        "What about the medical certificate?"
    )

    history.add_message(
        "assistant",
        "A medical certificate may be required for longer absences."
    )

    formatted_history = (
        history.format_for_prompt()
    )

    assert "sick leave" in formatted_history.lower()

    assert "medical certificate" in formatted_history.lower()


# ======================================================================
# STAGE 20.5 SUMMARY
# ======================================================================


def test_stage20_components_are_available():

    assert callable(
        rewrite_query
    )

    assert callable(
        extract_sources
    )

    assert ConversationHistory is not None

    assert RAGResponse is not None

    assert SourceReference is not None