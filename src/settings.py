from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # ======================
    # Embeddings
    # ======================

    embedding_model: str

    # ======================
    # LLM
    # ======================
    llm_model: str

    temperature: float
    # ======================
    # Retrieval
    # ======================

    top_k: int

    relevance_threshold: float


    max_history_messages: int = 10

    # ======================
    # Chunking
    # ======================
    chunk_size: int
    chunk_overlap: int

    # ======================
    # logging
    # ======================

    log_full_prompt: bool

    # ======================
    # Collection
    # # ======================

    collection_name: str

    model_config = SettingsConfigDict(
    env_file=PROJECT_ROOT / ".env",
    env_file_encoding="utf-8",
    extra="ignore",
)

settings = Settings()
