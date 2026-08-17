import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from src.api.exceptions import KnowledgeBaseException, LLMException, ValidationException
from src.api.handlers import (
    generic_exception_handler,
    knowledge_base_exception_handler,
    llm_exception_handler,
    validation_exception_handler,
)
from src.api.middleware import request_logging_middleware
from src.api.routes import router
from src.services.rag_service import RAGService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=" * 70)
    logger.info("Starting PDF Q&A Chatbot API...")
    logger.info("=" * 70)

    app.state.rag_service = RAGService()
    app.state.started_at = datetime.now(timezone.utc)

    logger.info("RAG Service initialized successfully.")

    yield

    logger.info("=" * 70)
    logger.info("Shutting down PDF Q&A Chatbot API...")
    logger.info("=" * 70)

    # Shutdown logic will be added here later.


app = FastAPI(
    title="PDF Q&A Chatbot API",
    description="Production-ready Retrieval Augmented Generation (RAG) API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)

app.add_exception_handler(ValidationException, validation_exception_handler)

app.add_exception_handler(KnowledgeBaseException, knowledge_base_exception_handler)

app.add_exception_handler(LLMException, llm_exception_handler)

app.add_exception_handler(Exception, generic_exception_handler)

app.middleware("http")(request_logging_middleware)
