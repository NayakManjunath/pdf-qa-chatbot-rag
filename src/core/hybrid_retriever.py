import logging

from rank_bm25 import BM25Okapi

from src.settings import settings

from src.core.splitter import split_documents
from src.core.retriever import search_documents
from src.core.reranker import rerank_documents

logger = logging.getLogger(__name__)

_BM25_INDEX = None
_DOCUMENT_CHUNKS = None

def load_bm25_index():

    """
        Build a BM 25 index from all documents chunks
    """

    global _BM25_INDEX
    global _DOCUMENT_CHUNKS

    chunks = split_documents()

    logger.info(" Building BM25 index from %d chunks",
            len(chunks),
    )
    logger.info(
        "Creating BM25 keyword index..."
    )

    tokenized_chunks = [

        chunk.page_content.split()
        for chunk in chunks

    ]

    bm25 = BM25Okapi(tokenized_chunks)

    _BM25_INDEX = bm25
    _DOCUMENT_CHUNKS = chunks

    logger.info(
        "BM25 index cached successfully."
    )

    return _BM25_INDEX, _DOCUMENT_CHUNKS


def bm25_search(
    query: str,
    top_k: int = 3,
    source: str | None = None,
):
    """
    Search documents using BM25 keyword retrieval.

    If a source is provided, only documents from that
    source are considered before selecting top_k results.
    """

    bm25, chunks = load_bm25_index()

    query_tokens = query.split()

    scores = bm25.get_scores(query_tokens)

    candidate_indices = []

    for index, score in enumerate(scores):

        if score <= 0:
            continue

        document = chunks[index]

        if source is not None:

            if document.metadata.get("filename") != source:
                continue

        candidate_indices.append(
            (index, score)
        )

    ranked_candidates = sorted(
        candidate_indices,
        key=lambda item: item[1],
        reverse=True,
    )

    top_candidates = ranked_candidates[:top_k]

    results = []

    for index, score in top_candidates:

        results.append(
            (
                chunks[index],
                score,
            )
        )

    logger.info(
        "BM25 retrieved %d document(s)",
        len(results),
    )

    return results



def reciprocal_rank_fusion(
    rank: int,
    k: int = 60,
) -> float:
    """
    Compute the Reciprocal Rank Fusion (RRF) score.

    Parameters
    ----------
    rank : int
        Rank of the document (starting from 1).

    k : int, default=60
        Constant used to reduce the influence of rank.

    Returns
    -------
    float
        RRF score.
    """

    return 1 / (k + rank)


def hybrid_search(
    query: str,
    top_k: int = 3,
    source: str | None = None,
):
    """
    Perform Hybrid Retrieval using
    Vector Search + BM25 + Reciprocal Rank Fusion (RRF).
    """

    
    vector_result = search_documents(
        query,
        source=source,
        top_k=top_k,
    )

    vector_documents = vector_result.documents

    
    bm25_results = bm25_search(
        query=query,
        top_k=top_k,
        source=source,
    )

    
    document_scores = {}

    
    for rank, document in enumerate(
        vector_documents,
        start=1,
    ):

        key = document.page_content

        document_scores[key] = {
            "document": document,
            "score": reciprocal_rank_fusion(rank),
        }

    
    for rank, (document, _) in enumerate(
        bm25_results,
        start=1,
    ):

        key = document.page_content

        score = reciprocal_rank_fusion(rank)

        if key in document_scores:

            document_scores[key]["score"] += score

        else:

            document_scores[key] = {
                "document": document,
                "score": score,
            }

    
    ranked_results = sorted(
        document_scores.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    

    combined_documents = [
        item["document"]
        for item in ranked_results
    ]

    logger.info("Running Cross-Encoder reranker...")

    reranked_results = rerank_documents(
        query=query,
        documents=combined_documents,
        top_k=top_k,
    )


    best_score = reranked_results[0][1]
    # best_score = reranked_results[0][1]
    
    logger.info(
            "Best Reranker Score : %.4f",
            best_score,
        )
    
    logger.info(
            "Relevance Threshold : %.4f",
            settings.relevance_threshold,
        )
    
    logger.info(
            "Retrieval Relevant : %s",
            is_relevant(best_score),
        )

    combined_documents = [
    document
    for document, _ in reranked_results
    ]

    
    logger.info("=" * 70)
    logger.info("HYBRID RETRIEVAL SUMMARY")
    logger.info("=" * 70)

    logger.info(
        "Vector Results : %d",
        len(vector_documents),
    )

    logger.info(
        "BM25 Results   : %d",
        len(bm25_results),
    )

    logger.info(
        "Final Results  : %d",
        len(combined_documents),
    )

    logger.info("=" * 70)

    return combined_documents

def is_relevant(score: float) -> bool:
        return score >= settings.relevance_threshold


def display_results(title: str, results):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    for rank, (document, score) in enumerate(results, start=1):

        print(f"\nRank #{rank}")
        print("-" * 60)
        print(f"BM25 Score : {score:.3f}\n")

        preview = document.page_content.strip()
        print(preview[:250])

        print("\nSource :", document.metadata["filename"])
        print("Page   :", document.metadata["page_label"])

def hybrid_search_with_scores(
    query: str,
    top_k: int = 3,
    source: str | None = None,
):
    """
    Perform hybrid retrieval and return
    documents together with Cross-Encoder scores.

    This function is used when the application
    needs retrieval confidence information.
    """

    vector_result = search_documents(
        query,
        source=source,
        top_k=top_k,
    )

    vector_documents = vector_result.documents

    bm25_results = bm25_search(
        query=query,
        top_k=top_k,
        source=source,
    )

    document_scores = {}

    # --------------------------------------------------
    # Vector Retrieval
    # --------------------------------------------------

    for rank, document in enumerate(
        vector_documents,
        start=1,
    ):

        key = document.page_content

        document_scores[key] = {
            "document": document,
            "score": reciprocal_rank_fusion(rank),
        }

    # --------------------------------------------------
    # BM25 Retrieval
    # --------------------------------------------------

    for rank, (document, _) in enumerate(
        bm25_results,
        start=1,
    ):

        key = document.page_content

        score = reciprocal_rank_fusion(rank)

        if key in document_scores:

            document_scores[key]["score"] += score

        else:

            document_scores[key] = {
                "document": document,
                "score": score,
            }

    # --------------------------------------------------
    # RRF Ranking
    # --------------------------------------------------

    ranked_results = sorted(
        document_scores.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    combined_documents = [
        item["document"]
        for item in ranked_results
    ]

    # --------------------------------------------------
    # Cross-Encoder Reranking
    # --------------------------------------------------

    logger.info(
        "Running Cross-Encoder reranker..."
    )

    reranked_results = rerank_documents(
        query=query,
        documents=combined_documents,
    )

    logger.info(
        "Hybrid retrieval with scores completed."
    )

    return reranked_results


if __name__ == "__main__":

    query = "How many annual leave days do employees receive?"
    query = "What is the company's office relocation policy?"
    query = "How many days of paid leave are available when an employee is sick?"
   
    

    results = hybrid_search(query)

    print()

    print("=" * 70)
    print("HYBRID SEARCH TEST")
    print("=" * 70)

    for rank, document in enumerate(results, start=1):

        print(f"\n## Rank #{rank}")
        print(document.page_content[:300])

        print(
            f"\nSource : "
            f"{document.metadata.get('filename')}"
        )

        print(
            f"Page : "
            f"{document.metadata.get('page_label')}"
        )


    
# if __name__ == "__main__":

#     print(">>> ENTERED HYBRID_SEARCH TEST <<<")

#     results = hybrid_search_with_scores(
#         query="How many sick leave days are employees entitled to?"
#     )

#     print()
#     print("=" * 70)
#     print("HYBRID RETRIEVAL WITH SCORES")
#     print("=" * 70)

#     for rank, (document, score) in enumerate(
#         results,
#         start=1,
#     ):

#         print()
#         print(f"Rank #{rank}")
#         print("-" * 70)

#         print(
#             f"Reranker Score : {score:.4f}"
#         )

#         print(
#             f"Source : "
#             f"{document.metadata.get('filename')}"
#         )

#         print(
#             f"Page : "
#             f"{document.metadata.get('page_label')}"
#         )

#     print("=" * 70)



# if __name__ == "__main__":

#     documents = hybrid_search(


#         """
#         annual leave policy

#         How many annual leave days do employees receive?

#         How many sick leave days are employees entitled to?

#         What is the yearly paid sick leave allowance for an employee?

#         How long is maternity leave?

#         What is the company's refund policy?
#         """

#         #  "What is the company's refund policy?",
#         # source="employee_handbook.pdf",
#         # "How long is maternity leave?",
#         # source="employee_handbook.pdf",
#         # "What is the yearly paid sick leave allowance for an employee?",
#         # source="employee_handbook.pdf",

#         # "How many sick leave days are employees entitled to?",
#         # source="employee_handbook.pdf",

#         # "How many annual leave days do employees receive?",
#         # source="employee_handbook.pdf",
#         # query="annual leave policy",
#         # source="employee_handbook.pdf",
#         # "annual leave policy"
#     )

#     print()
#     print("=" * 60)
#     print("HYBRID RETRIEVAL RESULTS")
#     print("=" * 60)

#     for rank, document in enumerate(documents, start=1):

#         print(f"\nRank #{rank}")
#         print("-" * 60)

#         preview = document.page_content.strip()

#         print(preview[:250])

#         print("\nSource :", document.metadata["filename"])
#         print("Page   :", document.metadata["page_label"])

   