from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value

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
