import os
from typing import Any

import requests


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


class APIClient:
    """HTTP client used by the Streamlit UI to communicate with FastAPI."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = (
            base_url
            or os.getenv("API_BASE_URL")
            or DEFAULT_API_BASE_URL
        ).rstrip("/")

        self.timeout = timeout

    def health_check(self) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/health",
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def ask_question(self, question: str) -> dict[str, Any]:
        """Send a question to the FastAPI /ask endpoint."""

        response = requests.post(
            f"{self.base_url}/ask",
            json={"question": question},
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()