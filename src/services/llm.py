import logging

logger = logging.getLogger(__name__)
from langchain_ollama import ChatOllama

from src.settings import settings


def create_llm():
    logger.info("Initializing Ollama LLM...")

    llm = ChatOllama(model=settings.llm_model, temperature=settings.temperature)
    logger.info("LLM initialized successfully.")
    return llm


if __name__ == "__main__":

    llm = create_llm()

    response = llm.invoke("What is MAchine Learning")

    print(response.content)
