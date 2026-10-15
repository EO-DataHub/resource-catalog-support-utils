"""
Caller authentication and workspace authorization.

The service writes into workspace storage with its own AWS role, which can write to any
workspace. So it must check for itself that the caller belongs to the workspace they ask
for, using the platform JWT forwarded by the ingress.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, PyJWKClientConnectionError, PyJWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

# The Keycloak client IDs platform tokens are issued for (the audience mappers on the eodh and
# eodh-workspaces clients, eodhp-argocd-deployment apps/keycloak/base/realms.yaml). This list is
# duplicated across the platform's services, so change them together.
JWT_AUDIENCE = ["eodh", "eodh-workspaces"]

# Workspace membership claims, from least to most privileged. Any of them grants access.
WORKSPACE_CLAIMS = ("workspaces", "workspaces-admin", "workspaces-owned")

bearer_scheme = HTTPBearer(auto_error=False)


class AuthError(Exception):
    """Raised when the caller is not authenticated or not allowed."""

    def __init__(self, message: str, *, code: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def unauthorized(message: str) -> AuthError:
    return AuthError(message, code="UNAUTHORIZED", status_code=status.HTTP_401_UNAUTHORIZED)


def forbidden(message: str) -> AuthError:
    return AuthError(message, code="FORBIDDEN", status_code=status.HTTP_403_FORBIDDEN)


def unavailable(message: str) -> AuthError:
    return AuthError(message, code="AUTH_UNAVAILABLE", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


async def auth_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Return auth errors in the same {error, code} shape as the other endpoint errors."""
    assert isinstance(exc, AuthError)
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc), "code": exc.code})


def check_auth_configured() -> None:
    """Fail at startup, rather than on the first notebook launch, if tokens can't be verified."""
    if not settings.keycloak_base_url:
        msg = "KEYCLOAK_BASE_URL must be set to verify JWTs"
        raise RuntimeError(msg)


@lru_cache
def _jwks_client() -> PyJWKClient:
    """One client per process, so Keycloak's signing keys are cached between requests."""
    certs_url = settings.keycloak_certs_url
    if not certs_url:
        msg = "KEYCLOAK_BASE_URL must be set to verify JWTs"
        raise RuntimeError(msg)
    return PyJWKClient(certs_url)


def get_token_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, Any]:
    """Verify the bearer JWT against Keycloak's published keys and return its claims.

    The signature is checked here rather than trusting the gateway, because traffic can also
    reach the service directly from inside the cluster.
    """
    if credentials is None:
        raise unauthorized("A bearer token is required")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(credentials.credentials)
        return jwt.decode(
            credentials.credentials,
            signing_key.key,
            audience=JWT_AUDIENCE,
            issuer=settings.keycloak_issuer,
            algorithms=["RS256"],
            options={"require": ["exp", "iss", "aud"]},
        )
    except PyJWKClientConnectionError as exc:
        # Keycloak is down or unreachable. This is not the caller's fault, so don't report
        # their token as invalid, which would send them round a re-login loop.
        logger.warning("Could not fetch Keycloak signing keys: %s", exc)
        raise unavailable("Token verification is temporarily unavailable") from exc
    except PyJWTError as exc:
        logger.info("Rejected bearer token: %s", exc)
        raise unauthorized("Invalid or expired token") from exc


TokenClaims = Annotated[dict[str, Any], Depends(get_token_claims)]


def _claim_list(claims: dict[str, Any], claim: str) -> list[str]:
    """Claims are lists, but a single-element claim may arrive as a bare string."""
    value = claims.get(claim)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple):
        return [item for item in value if isinstance(item, str)]
    return []


def authorize_workspace_user(claims: dict[str, Any], *, workspace_name: str, username: str) -> None:
    """Check the token belongs to `username` and that user is a member of `workspace_name`."""
    if claims.get("preferred_username") != username:
        raise forbidden("The username does not match the signed-in user")
    if not any(workspace_name in _claim_list(claims, claim) for claim in WORKSPACE_CLAIMS):
        raise forbidden(f"You are not a member of workspace '{workspace_name}'")
