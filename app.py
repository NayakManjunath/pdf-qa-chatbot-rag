from contextlib import asynccontextmanager

from fastapi import FastAPI

import logging
import src.logging_config

from src.api.routes import router
from src.services.rag_service import RAGService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application startup initiated")

    app.state.rag_service = RAGService()

    logger.info("RAG Service initiated Successfully")

    yield

    logger.info("Application shutdown successfully")

app = FastAPI(

    title = "PDF QA chatbot API",
    description = "A Retrieval Augumented Generation (RAG) API for answering questions from PDF documents",
    version = "1.0.0",
    lifespan = lifespan
)

app.include_router(router)

logger.info(" FastAPI application initiated Successfully")

