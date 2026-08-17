import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass

from langchain_core.documents import Document

from src.core.vectorstore import load_vector_store
from src.settings import settings


@dataclass
class RetrievalResult:
    documents: list[Document]
    best_distance: float
    average_distance: float
    worst_distance: float


def search_documents(
    query: str,
    source: str | None = None,
    top_k: int | None = None,
) -> RetrievalResult:

    vector_store = load_vector_store()

    search_kwargs = {
        "query": query,
        "k": top_k or settings.top_k,
    }

    # if source is not None:
    #     search_kwargs["filter"] = {
    #         "source": source,
    #     }

    if source:
        search_kwargs["filter"] = {
            "filename": source,
    }

    logger.info("Search Query : %s", query)

    if source:
        logger.info("Metadata Filter : %s", source)
    else:
        logger.info("Metadata Filter : None")

    # -----------------------------
    # Execute vector search
    # -----------------------------
    results = vector_store.similarity_search_with_score(
        **search_kwargs
    )

    # -----------------------------
    # No documents found
    # -----------------------------
    if not results:

        logger.warning("No documents retrieved.")

        return RetrievalResult(
            documents=[],
            best_distance=float("inf"),
            average_distance=float("inf"),
            worst_distance=float("inf"),
        )

    # -----------------------------
    # Calculate retrieval statistics
    # -----------------------------
    scores = [
        score
        for _, score in results
    ]

    best_distance = min(scores)
    worst_distance = max(scores)
    average_distance = sum(scores) / len(scores)

    logger.info(
        "Best Retrieval Distance : %.4f",
        best_distance,
    )

    documents = [
        document
        for document, _ in results
    ]

    return RetrievalResult(
        documents=documents,
        best_distance=best_distance,
        average_distance=average_distance,
        worst_distance=worst_distance,
    )


if __name__ == "__main__":

    
    # result = search_documents(
    #     query="leave policy",
    #     source=r"D:\Developments\Data_Science_Projects\pdf-qa-chatbot-clean\documents\employee_handbook.pdf",
    # )

    # print(f"\nRetrieved {len(result.documents)} document(s)")
    # print(f"\nBest Distance : {result.best_distance}")

    # for i, doc in enumerate(result.documents, start=1):

    #     print(f"\nDocument {i}")
    #     print("-" * 60)
    #     print(doc.page_content[:250])
    #     print("\nMetadata:")
    #     print(doc.metadata)

    # if __name__ == "__main__":

    result = search_documents(
        query="annual leave policy",
    )

    print(f"\nRetrieved {len(result.documents)} document(s)")

    for i, doc in enumerate(result.documents, start=1):

        print(f"\nDocument {i}")
        print("-" * 60)

        print(doc.page_content[:200])

        print("\nMetadata:")
        print(doc.metadata)