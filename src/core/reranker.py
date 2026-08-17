import logging

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

_RERANKER = None

def load_reranker():

    """ 
        Load the Cross_ Encoder reranker model

        the model is loaded only  once and then cached 
    """

    global _RERANKER

    if _RERANKER is None :

        logger.info(
        " Loading Cross-Encoder  reranker..."
        )

        _RERANKER = CrossEncoder(

            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        logger.info(
            "Cross-Encoder loaded successfully."
        )
    return _RERANKER



def rerank_documents(
    query: str,
    documents,
    top_k: int = 3,
):
    """
        Rerank retrieved documents using the Cross- Encoder.
    """

    model = load_reranker()

    pairs = [

    (
        query,
        document.page_content,
    )

    for document in documents

]
    logger.info(
        " Scoring %d  retrieved documents..",
        len(documents)
    )

    scores = model.predict(pairs)

    results = list(
        zip(
            documents,
            scores,
        )
    )
    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    # Keep only the Top-K highest scored documents
    results = results[:top_k]

    for rank, (document, score) in enumerate(
        results,
        start=1,
    ):
        logger.info(
            "Rerank #%d | Score: %.4f | Source: %s",
            rank,
            score,
            document.metadata.get("filename"),
        )

    logger.info(
        "Cross-Encoder reranked %d document(s).",
        len(results),
    )

    return results

if __name__ == "__main__":

    from src.core.hybrid_retriever import hybrid_search

    documents = hybrid_search(
    "How many sick leave days are employees entitled to?"
)

    print(type(documents))
    print(type(documents[0]))

    results = rerank_documents(
        "How many sick leave days are employees entitled to?",
        documents,
    )

    print()
    print("=" * 60)
    print("RERANK RESULTS")
    print("=" * 60)

    for rank, (document, score) in enumerate(results, start=1):

        print(f"\nRank #{rank}")
        print("-" * 60)
        print(f"Score : {score:.4f}\n")

        print(document.page_content[:200])

        print("\nSource:", document.metadata["filename"])