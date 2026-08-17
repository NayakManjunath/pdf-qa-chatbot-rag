import logging

from src.core.hybrid_retriever import hybrid_search

logger = logging.getLogger(__name__)

def compress_documents(
    query,
    documents,
):
    """
    Compress retrieved documents before sending them to the LLM.

    Currently keeps the first 300 characters of each document
    while preserving the original document metadata.
    """

    logger.info("=" * 70)
    logger.info("CONTEXT COMPRESSION")
    logger.info("=" * 70)

    logger.info(
        "Original Documents : %d",
        len(documents),
    )

    compressed_documents = []

    for document in documents:

        compressed_text = document.page_content.strip()[:300]

        compressed_document = document.model_copy(
            update={
                "page_content": compressed_text
            }
        )

        compressed_documents.append(
            compressed_document
        )

    logger.info(
        "Compressed Documents: %d",
        len(compressed_documents),
    )

    if compressed_documents:

        logger.info(
            "Characters per first chunk : %d",
            len(compressed_documents[0].page_content),
        )

    logger.info("Compression completed.")
    logger.info("=" * 70)

    return compressed_documents



if __name__ == "__main__":


    documents = hybrid_search(

    "How many sick leave days are employees entitled to?"
    )

    compressed = compress_documents(

        "How many sick leave days are employees entitled to?",
        documents,
    )

    print()

    print("=" *60)

    print("COMPRESSED DOCUMENTS")

    print("=" * 60)

    print(
        f"Returned {len(compressed)} documents."
    )


# def compress_documents(
#     query: str,
#     documents,
# ):
#     """
#     Compress retrieved documents before sending them to the LLM.

#     Currently this is a placeholder that simply returns
#     the retrieved documents unchanged.
#     """

#     logger.info("=" * 70)
#     logger.info("CONTEXT COMPRESSION")

#     logger.info("=" * 70)

#     logger.info(
#         "Original Documents : %d",
#         len(documents),
#     )

#     compressed_documents = documents

#     logger.info(
#         "Compressed Documents: %d",
#         len(compressed_documents),
#     )

#     logger.info("Compression completed.")
#     logger.info("=" *70)

#     return compressed_documents