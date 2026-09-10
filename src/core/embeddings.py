import logging
from functools import lru_cache
from pathlib import Path

import src.logging_config
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.splitter import split_documents
from src.settings import settings

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EMBEDDING_MODEL_PATH = (
    PROJECT_ROOT / "models" / "embedding" / "all-MiniLM-L6-v2"
)


@lru_cache(maxsize=1)
def get_embedding_model():
    logger.info(
        "Loading local HuggingFace embedding model: %s",
        EMBEDDING_MODEL_PATH,
    )

    return HuggingFaceEmbeddings(
        model_name=str(EMBEDDING_MODEL_PATH),
        model_kwargs={"local_files_only": True},
    )


def generate_sample_embedding():

    chunks = split_documents()

    embedding_model = get_embedding_model()

    embedding = embedding_model.embed_query(
        chunks[0].page_content
    )

    return embedding


if __name__ == "__main__":

    embedding = generate_sample_embedding()

    print(f"Embedding Dimension: {len(embedding)}")

    print("\nFirst 10 values\n")

    print(embedding[:10])