import logging

import src.logging_config

from src.core.conversation import ConversationHistory
from src.core.query_rewriter import rewrite_query


logger = logging.getLogger(__name__)


def print_result(
    test_name: str,
    original_query: str,
    rewritten_query: str,
):
    print()
    print("=" * 70)
    print(test_name)
    print("=" * 70)

    print()
    print("Original Query:")
    print(original_query)

    print()
    print("Rewritten Query:")
    print(rewritten_query)

    print("=" * 70)


# ================================================================
# TEST 1: STANDALONE QUERY
# ================================================================

def test_standalone_query():

    query = (
        "How many sick leave days are employees entitled to?"
    )

    history = ""

    result = rewrite_query(
        query=query,
        conversation_history=history,
    )

    print_result(
        "20.6 TEST 1 - STANDALONE QUERY",
        result.original_query,
        result.rewritten_query,
    )

    assert result.original_query == query

    assert result.rewritten_query == query

    assert result.was_rewritten is False


# ================================================================
# TEST 2: CONVERSATIONAL FOLLOW-UP
# ================================================================

def test_follow_up_query():

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

    query = (
        "What about the medical certificate?"
    )

    result = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    print_result(
        "20.6 TEST 2 - CONVERSATIONAL FOLLOW-UP",
        result.original_query,
        result.rewritten_query,
    )

    assert result.original_query == query

    assert result.rewritten_query.strip()

    assert result.was_rewritten is True

    assert "medical certificate" in (
        result.rewritten_query.lower()
    )


# ================================================================
# TEST 3: NEW TOPIC AFTER CONVERSATION
# ================================================================

def test_new_topic():

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

    query = (
        "What are the company's working hours?"
    )

    result = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    print_result(
        "20.6 TEST 3 - NEW TOPIC",
        result.original_query,
        result.rewritten_query,
    )

    assert result.original_query == query

    assert result.rewritten_query.strip()

    assert "working hours" in (
        result.rewritten_query.lower()
    )

    # The new topic should not incorrectly become
    # a sick-leave query.
    assert "sick leave" not in (
        result.rewritten_query.lower()
    )


# ================================================================
# TEST 4: MULTI-TURN FOLLOW-UP
# ================================================================

def test_multi_turn_follow_up():

    history = ConversationHistory(
        max_messages=10
    )

    history.add_message(
        "user",
        "Can employees work remotely?"
    )

    history.add_message(
        "assistant",
        "Employees may work remotely with manager approval."
    )

    query = (
        "What approval is needed?"
    )

    result = rewrite_query(
        query=query,
        conversation_history=history.format_for_prompt(),
    )

    print_result(
        "20.6 TEST 4 - MULTI-TURN FOLLOW-UP",
        result.original_query,
        result.rewritten_query,
    )

    assert result.rewritten_query.strip()

    assert result.was_rewritten is True

    assert "approval" in (
        result.rewritten_query.lower()
    )


# ================================================================
# MAIN EXECUTION
# ================================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("STAGE 20.6 - CONVERSATIONAL QUERY TESTS")
    print("=" * 70)

    test_standalone_query()

    test_follow_up_query()

    test_new_topic()

    test_multi_turn_follow_up()

    print()
    print("=" * 70)
    print("STAGE 20.6 TESTS COMPLETED")
    print("=" * 70)
    