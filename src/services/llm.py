import logging

from langchain_ollama import ChatOllama

from src.settings import settings


logger = logging.getLogger(__name__)


def create_llm():
    logger.info("Initializing Ollama LLM...")

    llm = ChatOllama(
        model=settings.llm_model,
        temperature=settings.temperature,
        base_url=settings.ollama_base_url,
    )

    logger.info(
        "Ollama LLM initialized successfully. Model=%s, BaseURL=%s",
        settings.llm_model,
        settings.ollama_base_url,
    )

    return llm

if __name__ == "__main__":

    llm = create_llm()

    response = llm.invoke("What is Machine Learning?")

    print(response.content)
