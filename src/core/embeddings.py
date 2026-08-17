import logging 

import src.logging_config

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from src.core.splitter import split_documents

from src.settings import settings

logger =  logging.getLogger(__name__)

@lru_cache(maxsize= 1)

def get_embedding_model():

    logger.info(

        "Loading HuggingFace embedding model..."
    )

    return HuggingFaceEmbeddings(

        model_name = settings.embedding_model
    )

def generate_sample_embedding():

    chunks = split_documents()

    embedding_model = get_embedding_model()

    embedding =  embedding_model.embed_query(

        chunks[0].page_content
    )

    return embedding

if __name__ == "__main__":

    embedding = generate_sample_embedding()

    print(f"Embedding Dimension: {len(embedding)}")

    print("\n FIrat 10  values\n")

    print(embedding[:10])


# from langchain_huggingface import HuggingFaceEmbeddings

# from src.core.splitter import split_documents
# from src.settings import settings


# def get_embedding_model():

#     embedding_model = HuggingFaceEmbeddings(model_name=settings.embedding_model)

#     return embedding_model


# def generate_sample_embedding():

#     chunks = split_documents()

#     embedding_model = get_embedding_model()

#     embedding = embedding_model.embed_query(chunks[0].page_content)

#     return embedding


# if __name__ == "__main__":

#     embedding = generate_sample_embedding()

#     print(f"Embedding Dimension: {len(embedding)}")

#     print("\nFirst 10 Values\n")

#     print(embedding[:10])
