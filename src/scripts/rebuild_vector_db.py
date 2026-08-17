import logging
import shutil

from src.config import VECTOR_DB_DIR
from src.core.vectorstore import create_vector_store
# from src.logging_config import setup_logging

# setup_logging()

logger = logging.getLogger(__name__)

def rebuild_vector_database():
    """
    Delete the existing vector database and rebuild it.
    """

    logger.info("=" * 70)
    logger.info("REBUILDING VECTOR DATABASE")
    logger.info("=" * 70)

    if VECTOR_DB_DIR.exists():

        logger.info("Removing existing vector database...")

        shutil.rmtree(VECTOR_DB_DIR)

    # create_vector_store()

    db = create_vector_store()

    logger.info("Collection Count : %d", db._collection.count())

    logger.info("=" * 70)
    logger.info("VECTOR DATABASE REBUILT SUCCESSFULLY")
    logger.info("=" * 70)


if __name__ == "__main__":

    rebuild_vector_database()