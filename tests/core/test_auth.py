"""Token verification and workspace checks on the notebook launch endpoint."""

from __future__ import annotations

import time
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.api.v1 import notebooks
from app.app_factory import create_app
from app.core import auth
from app.core.config import settings
from app.main import app
from app.services.notebook_launch_service import NotebookLaunchResult

client = TestClient(app)

_signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

PAYLOAD = {
    "workspace_name": "sparkgeotest",
    "username": "geodowd",
    "action_name": "pin_set_starter",
    "template_url": "https://example.com/templates/pin_set_starter.ipynb",
}


class _FakeLaunchService:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def launch_notebook(self, **kwargs: Any) -> NotebookLaunchResult:  # noqa: ANN401
        self.calls.append(kwargs)
        return NotebookLaunchResult(
            servername="pin_set_starter_1",
            notebook_path="jupyter/pin_set_starter_1.ipynb",
            spawn_url="https://hub.example/notebooks/hub/spawn/geodowd/pin_set_starter_1",
        )


class _FakeJwksClient:
    def get_signing_key_from_jwt(self, _token: str) -> SimpleNamespace:
        return SimpleNamespace(key=_signing_key.public_key())


@pytest.fixture(autouse=True)
def service(monkeypatch: pytest.MonkeyPatch) -> Iterator[_FakeLaunchService]:
    fake = _FakeLaunchService()
    app.dependency_overrides[notebooks.get_notebook_launch_service] = lambda: fake
    monkeypatch.setattr(auth, "_jwks_client", lambda: _FakeJwksClient())
    yield fake
    app.dependency_overrides.pop(notebooks.get_notebook_launch_service, None)


def _token(key: rsa.RSAPrivateKey = _signing_key, /, **overrides: Any) -> str:  # noqa: ANN401
    claims = {
        "preferred_username": "geodowd",
        "workspaces": ["sparkgeotest"],
        "aud": "eodh",
        "iss": settings.keycloak_issuer,
        "exp": int(time.time()) + 300,
        **overrides,
    }
    claims = {name: value for name, value in claims.items() if value is not None}
    return jwt.encode(claims, key, algorithm="RS256")


def _launch(token: str | None) -> Any:  # noqa: ANN401
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post("/api/v1/notebooks/launch", json=PAYLOAD, headers=headers)


def test_member_can_launch(service: _FakeLaunchService) -> None:
    response = _launch(_token())
    assert response.status_code == 200
    assert service.calls[0]["workspace_name"] == "sparkgeotest"


@pytest.mark.parametrize("claim", ["workspaces-admin", "workspaces-owned"])
def test_admins_and_owners_can_launch(claim: str) -> None:
    response = _launch(_token(workspaces=[], **{claim: ["sparkgeotest"]}))
    assert response.status_code == 200


def test_single_workspace_claim_as_string() -> None:
    assert _launch(_token(workspaces="sparkgeotest")).status_code == 200


def test_missing_token_is_rejected(service: _FakeLaunchService) -> None:
    response = _launch(None)
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"
    assert service.calls == []


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(lambda: "not-a-jwt", id="malformed"),
        pytest.param(lambda: _token(_other_key), id="wrong-signature"),
        pytest.param(lambda: _token(exp=int(time.time()) - 60), id="expired"),
        pytest.param(lambda: _token(aud="someone-else"), id="wrong-audience"),
        pytest.param(lambda: _token(exp=None), id="no-expiry"),
        pytest.param(lambda: _token(iss="https://elsewhere.example/keycloak/realms/eodhp"), id="wrong-issuer"),
        pytest.param(lambda: _token(iss=None), id="no-issuer"),
    ],
)
def test_invalid_token_is_rejected(token: Any, service: _FakeLaunchService) -> None:  # noqa: ANN401
    response = _launch(token())
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"
    assert service.calls == []


def test_other_workspace_is_forbidden(service: _FakeLaunchService) -> None:
    response = _launch(_token(workspaces=["another-workspace"]))
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
    assert service.calls == []


def test_workspace_name_is_not_matched_as_substring() -> None:
    assert _launch(_token(workspaces="sparkgeotest-other")).status_code == 403


def test_other_username_is_forbidden(service: _FakeLaunchService) -> None:
    response = _launch(_token(preferred_username="someone-else"))
    assert response.status_code == 403
    assert service.calls == []


class _UnreachableJwksClient:
    def get_signing_key_from_jwt(self, _token: str) -> SimpleNamespace:
        raise jwt.PyJWKClientConnectionError("Fail to fetch data from the url")


def test_keycloak_outage_is_unavailable_not_unauthorized(
    monkeypatch: pytest.MonkeyPatch, service: _FakeLaunchService
) -> None:
    monkeypatch.setattr(auth, "_jwks_client", lambda: _UnreachableJwksClient())
    response = _launch(_token())
    assert response.status_code == 503
    assert response.json()["code"] == "AUTH_UNAVAILABLE"
    assert service.calls == []


def test_app_refuses_to_start_without_keycloak(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "keycloak_base_url", None)
    with pytest.raises(RuntimeError, match="KEYCLOAK_BASE_URL"):
        create_app()
