from datetime import datetime

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str

class Citation(BaseModel):

    file: str

    page: int

class ResponseMetadata(BaseModel):
    retrieved_documents: int
    retrieval_distance: float
    llm_model: str
    embedding_model: str

class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[Citation]
    metadata: ResponseMetadata



class HealthResponse(BaseModel):

    status: str
    service: str
    version: str
    started_at: datetime
    uptime_seconds: int


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """

    error: str
    message: str
