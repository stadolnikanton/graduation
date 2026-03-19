import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.errors import DomainError

logger = logging.getLogger("filecloud")


async def domain_error_handler(request: Request, exc: DomainError):
    logger.warning(f"{exc.__class__.__name__}: {exc.message}")
    return JSONResponse(
        content={"status": exc.status_code, "error": exc.message},
        status_code=exc.status_code,
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(DomainError, domain_error_handler)
