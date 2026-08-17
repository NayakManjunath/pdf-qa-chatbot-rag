import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.api.exceptions import (
    KnowledgeBaseException,
    LLMException,
    ValidationException,
)

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: ValidationException):
    logger.warning("Validation error :%s,", exc)

    return JSONResponse(
        status_code=400, content={"error": "Validation Error", "message": "str(exc)"}
    )


async def knowledge_base_exception_handler(
    request: Request, exc: KnowledgeBaseException
):
    logger.exception("Knowledge base error: %s", exc)

    return JSONResponse(
        status_code=503, content={"error": "Knowledge Base Error", "message": str(exc)}
    )


async def llm_exception_handler(request: Request, exc: LLMException):
    logger.exception("LLM error: %s", exc)

    return JSONResponse(
        status_code=503, content={"error": "LLM error", "message": str(exc)}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandledexception : %s", exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": (" An unexpected error occured "),
        },
    )
