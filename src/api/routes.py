import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from src.api.dependencies import get_rag_service
from src.api.schemas import (
    AnswerResponse,
    ErrorResponse,
    HealthResponse,
    QuestionRequest,
)
from src.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/ask",
    response_model=AnswerResponse,
    summary="Ask questions about uploaded PDF documents",
    description=(
        "Retrieves relevant document chunks using Retrieval-Augmented "
        "Generation (RAG) and generates an answer using the configured LLM."
    ),
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Validation Error (e.g. empty question)",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation Error",
                        "message": "Question cannot be empty.",
                    }
                }
            },
        },
        503: {
            "model": ErrorResponse,
            "description": "Service unavailable (Knowledge Base or LLM)",
            "content": {
                "application/json": {
                    "examples": {
                        "knowledge_base": {
                            "summary": "Knowledge Base Error",
                            "value": {
                                "error": "Knowledge Base Error",
                                "message": "Unable to retrieve documents.",
                            },
                        },
                        "llm": {
                            "summary": "LLM Error",
                            "value": {
                                "error": "LLM Error",
                                "message": "Unable to generate response.",
                            },
                        },
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred.",
                    }
                }
            },
        },
    },
)
def ask_questions(
    question: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service),  # noqa: B008
):
    logger.info("Received POST request at /ask endpoint")

    response = rag_service.ask(question.question)

    logger.info("Successfully processed question.")

    return AnswerResponse(
        answer=response["answer"],
        confidence=response["confidence"],
        citations=response["citations"],
        metadata=response["metadata"],
    )

@router.get("/health", response_model=HealthResponse)
def health(request: Request):

    started_at = request.app.state.started_at

    now = datetime.now(timezone.utc)

    uptime = int((now - started_at).total_seconds())

    return HealthResponse(
        status="healthy",
        service="PDF Q&A Chatbot API",
        version="1.0.0",
        started_at=started_at,
        uptime_seconds=uptime,
    )

