from collections import deque


class ConversationMemory:
    """
    Stores recent conversation history.

    Only the latest N messages are kept.
    """

    def __init__(self, max_messages: int = 10):

        self.history = deque(maxlen=max_messages)

    def add_user_message(self, message: str):

        self.history.append(
            {
                "role": "User",
                "content": message,
            }
        )

    def add_ai_message(self, message: str):

        self.history.append(
            {
                "role": "Assistant",
                "content": message,
            }
        )

    def get_history(self) -> str:

        if not self.history:
            return ""

        return "\n".join(
            f"{item['role']}: {item['content']}"
            for item in self.history
        )

    def clear(self):

        self.history.clear()


if __name__ == "__main__":

    memory = ConversationMemory()

    memory.add_user_message(
        "What is the leave policy?"
    )

    memory.add_ai_message(
        "Employees receive 24 annual leave days."
    )

    memory.add_user_message(
        "How many sick leaves?"
    )

    print(memory.get_history())


# from collections import deque

# class ConversationMemory :

#     """
#         Stores recent conversation History

#         Only the latest N messages are kept 
#     """

# def __init__(self, max_message: int =10):

#     self.history = deque( maxlen=max_message)

# def add_user_message(self, message: str):

#         self.history.append(
#             {
#                 "role": "User",
#                 "content": message,
#             }
#         )

# def add_ai_message(self, message : str):

#     self.history.append(
#         {
#             "role": "Assistant",
#             "context" : message
#         }
#     )

# def get_history(self) -> str:

#     if not self.history:

#         return ""

#     return "\n".join(
#         f"{item['role']}.{item['context']}"
#         for item in self.history
#     )

# def clear(self):

#     self.history.clear()


# if __name__ == "__main__":

#     memory = ConversationMemory()

#     memory.add_user_message(
#         "What is the leave policy?"
#     )

#     memory.add_ai_message(
#         "Employees receive 24 annual leave days."
#     )

#     memory.add_user_message(
#         "How many sick leaves?"
#     )

#     print(memory.get_history())