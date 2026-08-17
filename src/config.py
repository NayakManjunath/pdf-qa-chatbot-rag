from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENT_DIR = PROJECT_ROOT / "documents"

VECTOR_DB_DIR = PROJECT_ROOT / "vectordb"

PDF_FILE = DOCUMENT_DIR / "employee_handbook.pdf"
