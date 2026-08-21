from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_stage24_integration(client, monkeypatch):
    """
    Final Stage 24 integration test.

    Verifies the complete FastAPI boundary:
    application startup,
    health endpoint,
    request validation,
    RAG endpoint integration,
    response contract,
    error contract,
    and request correlation ID.
    """

    # ------------------------------------------------------------------
    # 1. Application health
    # ------------------------------------------------------------------

    health_response = client.get("/health")

    assert health_response.status_code == 200

    health_data = health_response.json()

    assert health_data["status"] == "healthy"
    assert health_data["service"] == "PDF Q&A Chatbot API"
    assert health_data["version"] == "1.0.0"
    assert health_data["uptime_seconds"] >= 0

    datetime.fromisoformat(health_data["started_at"].replace("Z", "+00:00"))

    # ------------------------------------------------------------------
    # 2. Request validation
    # ------------------------------------------------------------------

    empty_response = client.post(
        "/ask",
        json={"question": "   "},
    )

    assert empty_response.status_code in (400, 422)

    empty_data = empty_response.json()

    assert "error" in empty_data or "detail" in empty_data

    # ------------------------------------------------------------------
    # 3. Request schema validation
    # ------------------------------------------------------------------

    invalid_response = client.post(
        "/ask",
        json={},
    )

    assert invalid_response.status_code in (400, 422)

    invalid_data = invalid_response.json()

    assert "error" in invalid_data or "detail" in invalid_data

    # ------------------------------------------------------------------
    # 4. RAG endpoint integration
    #
    # We replace the real RAGService operation so this test verifies
    # the API boundary without depending on Ollama, embeddings,
    # vector stores, or an actual PDF.
    # ------------------------------------------------------------------

    expected_result = {
        "answer": "The document contains information about machine learning.",
        "confidence": 0.92,
        "citations": [
            {
                "file": "sample.pdf",
                "page": 1,
            }
        ],
        "metadata": {
            "retrieved_documents": 2,
            "retrieval_distance": 0.18,
            "llm_model": "ollama",
            "embedding_model": "test-embedding-model",
        },
    }

    def fake_ask(question):
        assert question == "What does the document say about machine learning?"
        return expected_result

    monkeypatch.setattr(
        app.state.rag_service,
        "ask",
        fake_ask,
    )

    response = client.post(
        "/ask",
        json={
            "question": "What does the document say about machine learning?"
        },
    )

    # ------------------------------------------------------------------
    # 5. Successful API response
    # ------------------------------------------------------------------

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == expected_result["answer"]
    assert data["confidence"] == expected_result["confidence"]

    assert data["citations"] == expected_result["citations"]
    assert data["metadata"] == expected_result["metadata"]

    # ------------------------------------------------------------------
    # 6. Response contract
    # ------------------------------------------------------------------

    assert isinstance(data["answer"], str)
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["citations"], list)
    assert isinstance(data["metadata"], dict)

    assert "retrieved_documents" in data["metadata"]
    assert "retrieval_distance" in data["metadata"]
    assert "llm_model" in data["metadata"]
    assert "embedding_model" in data["metadata"]

    # ------------------------------------------------------------------
    # 7. Request correlation
    # ------------------------------------------------------------------

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) == 8

    # ------------------------------------------------------------------
    # 8. Error response contract
    # ------------------------------------------------------------------

    def failing_ask(question):
        from src.api.exceptions import LLMException

        raise LLMException("Unable to generate response.")

    monkeypatch.setattr(
        app.state.rag_service,
        "ask",
        failing_ask,
    )

    error_response = client.post(
        "/ask",
        json={
            "question": "Trigger an LLM failure"
        },
    )

    assert error_response.status_code == 503

    error_data = error_response.json()

    assert error_data["error"] == "LLM Error"
    assert error_data["message"] == "Unable to generate response."

    # Request ID should also be available for failed requests.
    error_request_id = error_response.headers.get("X-Request-ID")

    assert error_request_id is not None
    assert len(error_request_id) == 8