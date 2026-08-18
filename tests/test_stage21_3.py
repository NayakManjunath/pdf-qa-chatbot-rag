from src.core.conversation import ConversationHistory


def test_separate_conversations_have_independent_history():
    conversation_a = ConversationHistory(max_messages=10)
    conversation_b = ConversationHistory(max_messages=10)

    conversation_a.add_message(
        "user",
        "What is the annual leave policy?",
    )

    conversation_a.add_message(
        "assistant",
        "Employees receive annual leave according to company policy.",
    )

    conversation_b.add_message(
        "user",
        "What is the sick leave policy?",
    )

    conversation_b.add_message(
        "assistant",
        "Employees receive sick leave according to company policy.",
    )

    history_a = conversation_a.get_messages()
    history_b = conversation_b.get_messages()

    assert len(history_a) == 2
    assert len(history_b) == 2

    assert history_a[0].content == (
        "What is the annual leave policy?"
    )

    assert history_b[0].content == (
        "What is the sick leave policy?"
    )


def test_conversation_context_does_not_leak_between_sessions():
    conversation_a = ConversationHistory(max_messages=10)
    conversation_b = ConversationHistory(max_messages=10)

    conversation_a.add_message(
        "user",
        "Tell me about annual leave.",
    )

    conversation_a.add_message(
        "assistant",
        "Annual leave is provided according to company policy.",
    )

    history_b = conversation_b.format_for_prompt()

    assert history_b == ""

    assert "annual leave" not in history_b.lower()


def test_multi_turn_order_is_preserved():
    history = ConversationHistory(max_messages=10)

    history.add_message(
        "user",
        "What is the leave policy?",
    )

    history.add_message(
        "assistant",
        "The company provides different types of leave.",
    )

    history.add_message(
        "user",
        "What about sick leave?",
    )

    history.add_message(
        "assistant",
        "Employees receive sick leave according to policy.",
    )

    messages = history.get_messages()

    assert len(messages) == 4

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[3].role == "assistant"

    assert messages[0].content == (
        "What is the leave policy?"
    )

    assert messages[2].content == (
        "What about sick leave?"
    )


def test_conversation_can_be_reset_without_affecting_other_session():
    conversation_a = ConversationHistory(max_messages=10)
    conversation_b = ConversationHistory(max_messages=10)

    conversation_a.add_message(
        "user",
        "Tell me about annual leave.",
    )

    conversation_a.add_message(
        "assistant",
        "Annual leave information.",
    )

    conversation_b.add_message(
        "user",
        "Tell me about sick leave.",
    )

    conversation_b.add_message(
        "assistant",
        "Sick leave information.",
    )

    conversation_a.clear()

    assert conversation_a.get_messages() == []

    assert len(conversation_b.get_messages()) == 2

    assert (
        conversation_b.get_messages()[0].content
        == "Tell me about sick leave."
    )


def test_history_limit_is_enforced_per_conversation():
    conversation_a = ConversationHistory(max_messages=3)
    conversation_b = ConversationHistory(max_messages=3)

    for index in range(5):
        conversation_a.add_message(
            "user",
            f"Conversation A message {index}",
        )

    for index in range(2):
        conversation_b.add_message(
            "user",
            f"Conversation B message {index}",
        )

    messages_a = conversation_a.get_messages()
    messages_b = conversation_b.get_messages()

    assert len(messages_a) == 3
    assert len(messages_b) == 2

    assert messages_a[0].content == (
        "Conversation A message 2"
    )

    assert messages_a[-1].content == (
        "Conversation A message 4"
    )

    assert messages_b[0].content == (
        "Conversation B message 0"
    )