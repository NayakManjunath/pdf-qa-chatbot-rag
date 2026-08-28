import logging

import src.logging_config

from langchain_ollama import ChatOllama

from src.settings import settings


logger = logging.getLogger(__name__)

_LLM = None


def create_llm():
    logger.info("Initializing Ollama LLM...")

    llm = ChatOllama(
        model=settings.llm_model,
        temperature=settings.temperature,
    )

    logger.info("LLM initialized successfully.")

    return llm


def get_llm():
    """
    Return a cached LLM instance.

    The LLM is initialized only once per application
    process and reused for subsequent calls.
    """

    global _LLM

    if _LLM is None:
        logger.info("Creating cached LLM instance...")
        _LLM = create_llm()
    else:
        logger.debug("Using cached LLM instance.")

    return _LLM


if __name__ == "__main__":

    llm = get_llm()

    response = llm.invoke(
        "What is 2 + 2?"
    )

    print()
    print("=" * 60)
    print("LLM TEST")
    print("=" * 60)

    print(response.content)

# import logging

# import src.logging_config

# from langchain_ollama import ChatOllama

# from src.settings import settings

# logger = logging.getLogger(__name__)


# def get_llm():

#     logger.info("Loading LLM...")

#     llm = ChatOllama(
#         model=settings.llm_model,
#         temperature=settings.temperature,
#     )

#     logger.info("LLM loaded successfully.")

#     return llm


# if __name__ == "__main__":

#     llm = get_llm()

#     response = llm.invoke(
#         "What is 2 + 2?"
#     )

#     print()
#     print("=" * 60)
#     print("LLM TEST")
#     print("=" * 60)

#     print(response.content)
