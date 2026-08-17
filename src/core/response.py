import logging 
import src.logging_config

from langchain_core.documents import Document
import logging
from dataclasses import dataclass

import src.logging_config

from langchain_core.documents import Document


logger = logging.getLogger(__name__)


@dataclass
class SourceReference:
    filename: str
    page: str


@dataclass
class RAGResponse:
    answer: str
    sources: list[SourceReference]


def extract_sources(
    documents: list[Document],
) -> list[SourceReference]:
    """
    Extract source information directly from
    retrieved document metadata.
    """

    sources = []

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
            filename=filename,
            page=str(page),
        )

        if source not in sources:
            sources.append(source)

    logger.info(
        "Extracted %d unique source(s).",
        len(sources),
    )

    return sources

logger = logging.getLogger(__name__)

@dataclass 
class SourceReference :

    filename : str
    page : str 

@dataclass
class RAGResponse :

    answer  : str
    sources : list[SourceReference]

    def extract_sources(

            documents : list[Document]

        ) -> list[SourceReference]:

        """
             Extract sources information directly from retrieved document metadata

        """
        sources =[]

        for document in documents:

            filename = document.metadata.get(

                "filename",
                "unkonwn",
            )

        page= document.metadata.get(

            "page_label",
            document.metadata.get(
                "page",
                "unknown",
            ),
        )

        source = SourceReference(

            filename = filename,
            page = str([page]),
        )

        if source not in sources :

            sources.append(source)

        logger.info (
            "Extracted %d unique source(s)",
             len(sources),
        )

        return sources 