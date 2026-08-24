from pathlib import Path
import ui.app as app

import pytest

from ui.api_client import APIClient
from ui.config import (
    API_BASE_URL,
    API_TIMEOUT,
    APP_ICON,
    APP_TITLE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_DIR = PROJECT_ROOT / "ui"

# ---------------------------------------------------------------------------
# 25.1.1 Configuration foundation
# ---------------------------------------------------------------------------

def test_ui_configuration_is_available():
    assert APP_TITLE == "PDF Q&A Chatbot"
    assert APP_ICON == "📄"

    assert isinstance(API_BASE_URL, str)
    assert API_BASE_URL.startswith("http")

    assert isinstance(API_TIMEOUT, float)
    assert API_TIMEOUT > 0


# ---------------------------------------------------------------------------
# 25.1.2 API client initialization
# ---------------------------------------------------------------------------

def test_api_client_initializes_from_configuration():
    client = APIClient(
        base_url=API_BASE_URL,
        timeout=API_TIMEOUT,
    )

    assert client.base_url == API_BASE_URL.rstrip("/")
    assert client.timeout == API_TIMEOUT


# ---------------------------------------------------------------------------
# 25.1.3 API base URL normalization
# ---------------------------------------------------------------------------

def test_api_client_removes_trailing_slash():
    client = APIClient(
        base_url="http://127.0.0.1:8000/",
        timeout=30.0,
    )

    assert client.base_url == "http://127.0.0.1:8000"


# ---------------------------------------------------------------------------
# 25.1.4 Health-check HTTP boundary
# ---------------------------------------------------------------------------

def test_api_client_health_check(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "healthy",
                "service": "PDF Q&A Chatbot API",
                "version": "1.0.0",
                "started_at": "2026-08-24T00:00:00+00:00",
                "uptime_seconds": 10,
            }

    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "requests.get",
        fake_get,
    )

    client = APIClient(
        base_url="http://127.0.0.1:8000",
        timeout=30.0,
    )

    result = client.health_check()

    assert captured["url"] == "http://127.0.0.1:8000/health"
    assert captured["timeout"] == 30.0

    assert result["status"] == "healthy"
    assert result["service"] == "PDF Q&A Chatbot API"
    assert result["version"] == "1.0.0"
    assert result["uptime_seconds"] == 10


# ---------------------------------------------------------------------------
# 25.1.5 Health-check failure handling
# ---------------------------------------------------------------------------

def test_api_client_health_check_propagates_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise RuntimeError("Backend unavailable")

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(
        "requests.get",
        fake_get,
    )

    client = APIClient(
        base_url="http://127.0.0.1:8000",
        timeout=30.0,
    )

    with pytest.raises(RuntimeError, match="Backend unavailable"):
        client.health_check()


# ---------------------------------------------------------------------------
# 25.1.6 UI module existence
# ---------------------------------------------------------------------------

def test_ui_application_files_exist():
    assert (UI_DIR / "app.py").exists()
    assert (UI_DIR / "api_client.py").exists()
    assert (UI_DIR / "config.py").exists()
    assert (UI_DIR / "__init__.py").exists()


# ---------------------------------------------------------------------------
# 25.1.7 Streamlit application imports successfully
# ---------------------------------------------------------------------------

def test_streamlit_application_imports():
    assert hasattr(app, "main")
    assert callable(app.main)