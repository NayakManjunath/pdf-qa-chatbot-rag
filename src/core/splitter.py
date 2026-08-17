import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.loader import load_documents
from src.settings import settings

logger = logging.getLogger(__name__)


def split_documents():
    documents = load_documents()

    logger.info("Loading documents...")

    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=settings.chunk_sizehunk_size, chunk_overlap=settings.chunk_overlap
    # )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)

    logger.info(f"Created {len(chunks)} chunks.")

    return chunks


if __name__ == "__main__":

    chunks = split_documents()

    print(f"Total Chunks: {len(chunks)}")

    print("\n First Chunk:\n")

    print(chunks[0].page_content)

    print("\nMetaData\n")

    print(chunks[0].metadata)
