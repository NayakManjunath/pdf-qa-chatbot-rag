import logging
from dataclasses import dataclass

import src.logging_config

from langchain_core.documents import Document


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceReference:
    """
    Represents the source location used to generate
    a RAG answer.
    """

    filename: str
    page: str


@dataclass
class RAGResponse:
    """
    Final structured response returned by the RAG system.
    """

    answer: str
    sources: list[SourceReference]


def extract_sources(
    documents: list[Document],
) -> list[SourceReference]:
    """
    Extract unique source references from retrieved documents.

    Each source contains:
    - filename
    - page number / page label
    """

    sources: list[SourceReference] = []

    for document in documents:

        filename = document.metadata.get(
            "filename",
            "unknown",
        )

        page = document.metadata.get(
            "page_label",
            document.metadata.get(
                "page",
                "unknown",
            ),
        )

        source = SourceReference(
            filename=str(filename),
            page=str(page),
        )

        if source not in sources:
            sources.append(source)

    logger.info(
        "Extracted %d unique source(s).",
        len(sources),
    )

    return sources

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("STAGE 20.3 - RESPONSE / SOURCE EXTRACTION TEST")
    print("=" * 70)

    test_documents = [
        Document(
            page_content="Employee handbook content",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),
        Document(
            page_content="Another chunk from same page",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "1",
            },
        ),
        Document(
            page_content="Different page content",
            metadata={
                "filename": "employee_handbook.pdf",
                "page_label": "2",
            },
        ),
    ]

    sources = extract_sources(
        test_documents
    )

    print()
    print("Extracted Sources:")
    print("-" * 70)

    for index, source in enumerate(
        sources,
        start=1,
    ):
        print(
            f"{index}. "
            f"{source.filename}, "
            f"Page {source.page}"
        )

    print()
    print(
        f"Unique Sources: {len(sources)}"
    )

    print("=" * 70)
    print("STAGE 20.3 TEST COMPLETED")
    print("=" * 70)
