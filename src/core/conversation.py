from dataclasses import dataclass

@dataclass
class ChatMessage :
    role : str
    content : str


class ConversationHistory :

    def __init__(self, max_messages : int = 10):

        self.messages : list [ChatMessage] = []

        self.max_messages = max_messages

    def add_message (self, role : str, content : str):

        message = ChatMessage(
            role=role,
            content=content,
        )

        self.messages.append(message)

        if len(self.messages) > self.max_messages:

            self.messages.pop(0)

    def get_messages(self) -> list[ChatMessage]:

        return self.messages.copy()

    def clear(self):

        self.messages.clear()

    def format_for_prompt(self) -> str:

        formatted_messages = []

        for message in self.messages:

            formatted_messages.append(
                f"{message.role.upper()}: {message.content}"
            )

        return "\n".join(formatted_messages)


if __name__ == "__main__":

    history = ConversationHistory(max_messages=10)

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

    print("=" * 60)
    print("FORMATTED CONVERSATION")
    print("=" * 60)

    print(history.format_for_prompt())
