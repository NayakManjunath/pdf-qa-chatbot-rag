import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]

    request.state.request_id = request_id

    logger.info("=" * 70)
    logger.info("REQUEST START")
    logger.info("=" * 70)

    logger.info("Request ID : %s", request_id)
    logger.info("Method     : %s", request.method)
    logger.info("Path       : %s", request.url.path)

    client_ip = request.client.host if request.client else "Unknown"

    logger.info("Client IP  : %s", client_ip)

    logger.info("=" * 70)

    start_time = time.perf_counter()

    response = None

    try:
        response = await call_next(request)
        return response

    finally:
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        logger.info("=" * 70)
        logger.info("REQUEST END")
        logger.info("=" * 70)
        logger.info(f"Request ID     : {request_id}")

        if response is not None:
            logger.info(f"Status Code    : {response.status_code}")
        else:
            logger.info("Status Code    : Request terminated with exception")

        logger.info(f"Execution Time : {execution_time:.3f} seconds")
        logger.info("=" * 70)

        if response is not None:
            response.headers["X-Request-ID"] = request_id
