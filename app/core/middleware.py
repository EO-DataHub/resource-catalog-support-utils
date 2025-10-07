"""
Middleware configuration for the QLR Generator API.

This module contains all middleware components including request logging,
CORS configuration, and other cross-cutting concerns.
"""

import time
import logging
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .config import settings

logger = logging.getLogger(__name__)


def setup_cors_middleware(app):
    """
    Configure CORS middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allowed_origins,
        allow_origin_regex=settings.cors.origin_regex,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    logger.info("CORS middleware configured successfully")


async def request_logging_middleware(request: Request, call_next) -> Response:
    """
    Middleware to log all incoming requests with timing information.

    This middleware logs request details, processing time, and response status
    for monitoring and debugging purposes.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware/handler in the chain

    Returns:
        HTTP response with timing information
    """
    # Check if request logging is enabled
    if not settings.logging.log_requests:
        return await call_next(request)

    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Log request details
    logger.info(
        f"Request started: {request.method} {request.url.path} "
        f"from {client_ip} (User-Agent: {user_agent})"
    )

    # Log query parameters if present
    if request.query_params:
        logger.debug(f"Query params: {dict(request.query_params)}")

    # Log request body for POST/PUT requests if enabled
    if (
        settings.logging.log_request_body
        and request.method in settings.http.methods_to_log_body
    ):
        try:
            body = await request.body()
            if body:
                logger.debug(
                    f"Request body: {body.decode('utf-8')[: settings.logging.body_log_limit]}..."
                )
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")

    # Process the request
    try:
        response = await call_next(request)
    except Exception as e:
        # Log any unhandled exceptions
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"-> Exception: {str(e)} in {process_time:.3f}s"
        )
        raise

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response details
    status_emoji = (
        "✅"
        if 200 <= response.status_code < 300
        else "❌"
        if response.status_code >= 400
        else "⚠️"
    )
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"-> {response.status_code} {status_emoji} in {process_time:.3f}s"
    )

    # Add timing header to response
    response.headers[settings.http.timing_header] = str(round(process_time, 3))

    return response


def setup_middleware(app):
    """
    Set up all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Set up CORS middleware
    setup_cors_middleware(app)

    # Add request logging middleware
    app.middleware("http")(request_logging_middleware)

    logger.info("All middleware configured successfully")
