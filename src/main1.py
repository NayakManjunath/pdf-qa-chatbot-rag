# from services.rag_service import RAGService

# def main():
#     rag = RAGService()
#     while True:
#         question = input("\n Ask a Question (type 'exit' to quit)")

#         if question.lower() == "exit":
#             break

#         answer = rag.ask(question)
#         print("\n Answer:\n")
#         print(answer)

# if __name__ == "__main__":
#     main()

from src.settings import settings

print(settings.llm_model)
print(settings.top_k)
print(settings.embedding_model)
