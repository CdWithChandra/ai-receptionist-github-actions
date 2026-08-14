import logging
from fastapi  import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str, status_code: int =400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    logger.warning(
        "Application error | path=%s | status=%s | message=%s",
        request.url.path,
        exc.status_code,
        exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message
        },
    )

async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unexpected application error | path=%s",
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )