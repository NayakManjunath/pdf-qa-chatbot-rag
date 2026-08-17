import logging

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

from src.config import DOCUMENT_DIR

logger = logging.getLogger(__name__)


def load_documents():
    """
    Load all PDF documents from the documents directory.

    Returns
    -------
    list[Document]
        Documents loaded from every PDF found in the folder.
    """

    logger.info("Loading PDF documents...")

    # loader = PyPDFLoader(str(PDF_FILE))

    # documents = loader.load()
    documents = []

    pdf_files = list(DOCUMENT_DIR.glob("*.pdf"))

    if not pdf_files:

        raise FileNotFoundError(
            f"No PDF files found in {DOCUMENT_DIR}"
        )

    for pdf_file in pdf_files:

        logger.info(
            "Loading %s",
            pdf_file.name,
        )

        loader = PyPDFLoader(
            str(pdf_file)
        )

        pdf_documents = loader.load()

  
    for document in pdf_documents:

        document.metadata["filename"] = pdf_file.name

    documents.extend(pdf_documents)

    logger.info(f"Loaded {len(documents)} document(s).")

    return documents


if __name__ == "__main__":

    documents = load_documents()

    print(f"Total Pages Loaded:{len(documents)}")
    print("\nFirst Page\n")

    print(documents[0].page_content)
    print("\nMetaData")

    print(documents[0].metadata)
