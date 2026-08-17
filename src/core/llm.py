import logging

import src.logging_config

from langchain_ollama import ChatOllama

from src.settings import settings

logger = logging.getLogger(__name__)


def get_llm():

    logger.info("Loading LLM...")

    llm = ChatOllama(
        model=settings.llm_model,
        temperature=settings.temperature,
    )

    logger.info("LLM loaded successfully.")

    return llm


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