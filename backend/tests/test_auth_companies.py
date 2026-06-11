import pytest
from fastapi.testclient import TestClient

from app.core.database import reset_database
from app.main import app


@pytest.fixture(autouse=True)
def clean_database() -> None:
    reset_database()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def register_payload() -> dict[str, str]:
    return {
        "email": "owner@example.com",
        "password": "strong-password",
        "company_name": "Acme Ltda",
    }


def register_user(client: TestClient) -> dict:
    response = client.post("/auth/register", json=register_payload())
    assert response.status_code == 201
    return response.json()


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_register_creates_user_company_and_token(client: TestClient) -> None:
    data = register_user(client)

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"] == {
        "id": 1,
        "email": "owner@example.com",
        "company_id": 1,
    }
    assert data["company"] == {"id": 1, "name": "Acme Ltda"}


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    register_user(client)

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 409


def test_login_returns_token_for_valid_credentials(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "strong-password"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "owner@example.com"
    assert data["company"]["name"] == "Acme Ltda"


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    registered = register_user(client)

    response = client.get(
        "/auth/me",
        headers=auth_headers(registered["access_token"]),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "owner@example.com",
        "company_id": 1,
    }


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_current_company_returns_authenticated_users_company(client: TestClient) -> None:
    registered = register_user(client)

    response = client.get(
        "/companies/current",
        headers=auth_headers(registered["access_token"]),
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Acme Ltda"}


def test_current_company_requires_authentication(client: TestClient) -> None:
    response = client.get("/companies/current")

    assert response.status_code == 401
