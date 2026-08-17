from fastapi import Request

from src.services.rag_service import RAGService


def get_rag_service(
    request: Request,
) -> RAGService:
    """
    Return the shared RAGService instance stored in the FASTAPI application state
    """

    return request.app.state.rag_service
