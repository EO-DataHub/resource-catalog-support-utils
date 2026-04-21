"""
Middleware configuration for the Resource Catalog Support Utils API.

This module contains all middleware components including request logging,
CORS configuration, and other cross-cutting concerns.
"""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .config import settings

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Ensure '*' is not in origins when credentials are enabled
    origins = settings.cors.allowed_origins.copy()
    if settings.cors.allow_credentials and "*" in origins:
        origins = [origin for origin in origins if origin != "*"]
        logger.warning(
            "Removed '*' from allowed_origins because allow_credentials=True. "
            "CORS spec does not allow '*' with credentials."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    logger.info(
        f"CORS middleware configured successfully with origins: {origins}, "
        f"allow_credentials: {settings.cors.allow_credentials}"
    )


async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
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
    logger.info(f"Request started: {request.method} {request.url.path} from {client_ip} (User-Agent: {user_agent})")

    # Log query parameters if present
    if request.query_params:
        logger.debug(f"Query params: {dict(request.query_params)}")

    # Log request body for POST/PUT requests if enabled
    if settings.logging.log_request_body and request.method in settings.http.methods_to_log_body:
        try:
            body = await request.body()
            if body:
                logger.debug(f"Request body: {body.decode('utf-8')[: settings.logging.body_log_limit]}...")
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")

    # Process the request
    try:
        response = await call_next(request)
    except Exception as e:
        # Log any unhandled exceptions
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path} -> Exception: {e!s} in {process_time:.3f}s")
        raise

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response details
    status_emoji = "✅" if 200 <= response.status_code < 300 else "❌" if response.status_code >= 400 else "⚠️"
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"-> {response.status_code} {status_emoji} in {process_time:.3f}s"
    )

    # Add timing header to response
    response.headers[settings.http.timing_header] = str(round(process_time, 3))

    return response


async def cors_cleanup_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Middleware to clean up duplicate or malformed CORS headers.

    This is needed when running behind a proxy/load balancer (like in ECR deployments)
    that may add its own CORS headers, causing duplicate values.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware/handler in the chain

    Returns:
        HTTP response with cleaned CORS headers
    """
    response = await call_next(request)

    # Clean up Access-Control-Allow-Origin header if it contains multiple values
    if "access-control-allow-origin" in response.headers:
        origin_header = response.headers.get("access-control-allow-origin")

        # Check if header contains multiple values (comma-separated)
        if origin_header and "," in origin_header:
            # Split and filter out '*' and invalid values
            values = [v.strip() for v in origin_header.split(",")]

            # Remove '*' if present (not allowed with credentials)
            values = [v for v in values if v != "*"]

            # If we have valid origins, use the first one that matches our allowed list
            # Otherwise, use the first non-wildcard value
            if values:
                # Get the origin from the request
                request_origin = request.headers.get("origin")

                # If request origin is in our allowed list, use it
                if request_origin and request_origin in settings.cors.allowed_origins:
                    response.headers["access-control-allow-origin"] = request_origin
                elif values:
                    # Use the first valid origin from the header
                    response.headers["access-control-allow-origin"] = values[0]
                else:
                    # If no valid values, remove the header
                    del response.headers["access-control-allow-origin"]
            else:
                # No valid values, remove the header
                del response.headers["access-control-allow-origin"]

            logger.warning(
                f"Cleaned up malformed CORS header. Original: '{origin_header}', "
                f"Cleaned: '{response.headers.get('access-control-allow-origin', 'removed')}'"
            )

    return response


def setup_middleware(app: FastAPI) -> None:
    """
    Set up all middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Set up CORS middleware (runs first)
    setup_cors_middleware(app)

    # Add CORS cleanup middleware (runs after CORS middleware to clean up proxy-added headers)
    # This is especially important for ECR deployments behind load balancers/proxies
    app.middleware("http")(cors_cleanup_middleware)

    # Add request logging middleware
    app.middleware("http")(request_logging_middleware)

    logger.info("All middleware configured successfully")
