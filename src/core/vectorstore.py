import logging

from langchain_chroma import Chroma

from src.config import VECTOR_DB_DIR
from src.core.embeddings import get_embedding_model
from src.core.splitter import split_documents
from src.settings import settings

logger = logging.getLogger(__name__)

_VECTOR_STORE = None


def create_vector_store():

    chunks = split_documents()

    logger.info(
        "Preparing %d chunks for indexing.",
        len(chunks),
    )


    pdf_names = {
        chunk.metadata["filename"]
        for chunk in chunks
    }

    logger.info(
        "Detected %d PDF file(s).",
        len(pdf_names),
    )

    logger.info("=" * 70)
    logger.info("CREATING VECTOR DATABASE")
    logger.info("=" * 70)

    embedding_model = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(VECTOR_DB_DIR),
        collection_name=settings.collection_name,
    )

    
    logger.info("=" * 70)
    logger.info("VECTOR DATABASE CREATED")
    logger.info("=" * 70)

    logger.info(
        "Indexed %d chunks from %d PDF(s).",
        len(chunks),
        len(pdf_names),
    )
    logger.info("Vector database created successfully.")

    return vector_store


def load_vector_store():

    global _VECTOR_STORE

    if _VECTOR_STORE is None:

        logger.info(
            "Opening vector database..."
        )

        _VECTOR_STORE = Chroma(
            persist_directory=str(VECTOR_DB_DIR),
            embedding_function=get_embedding_model(),
            collection_name=settings.collection_name,
        )

        logger.info(
            "Vector database opened successfully."
        )

    else:

        logger.debug(
            "Using cached vector database."
        )

    return _VECTOR_STORE


if __name__ == "__main__":

    db = create_vector_store()

    print("Vector Database Created Successfully!")

    print()

    print("=" * 60)

    print(
        f"Collection Count : {db._collection.count()}"
    )

    print("=" * 60)