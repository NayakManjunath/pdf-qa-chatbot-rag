import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import src.logging_config
from fastapi import FastAPI

from src.api.routes import router
from src.services.rag_service import RAGService


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=" * 70)
    logger.info("Application startup initiated")
    logger.info("=" * 70)

    # Initialize shared RAG service.
    app.state.rag_service = RAGService()

    # Store application startup time for the health endpoint.
    app.state.started_at = datetime.now(timezone.utc)

    logger.info("RAG Service initialized successfully.")
    logger.info("Application startup completed successfully.")

    yield

    logger.info("=" * 70)
    logger.info("Application shutdown initiated")
    logger.info("=" * 70)

    logger.info("Application shutdown completed successfully.")


app = FastAPI(
    title="PDF Q&A Chatbot API",
    description=(
        "A Retrieval Augmented Generation (RAG) API "
        "for answering questions from PDF documents"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

logger.info("FastAPI application initialized successfully.")