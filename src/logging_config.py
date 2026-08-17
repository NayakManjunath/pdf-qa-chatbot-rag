import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

logging.getLogger("urllib3").setLevel(logging.WARNING)

logging.getLogger("chromadb").setLevel(logging.WARNING)
