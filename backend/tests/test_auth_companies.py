from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.database import create_sqlite_database, get_db
from app.main import app


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    database = create_sqlite_database()

    def override_get_db() -> Generator:
        yield database

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    database.connection.close()


def register_user(client: TestClient, email: str = "ana@example.com") -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple",
            "name": "Ana Silva",
            "company_name": "Lucro Saudável Ltda",
        },
    )
    assert response.status_code == 201
    return response.json()


def assert_password_hash_is_absent(payload: dict) -> None:
    assert "password_hash" not in payload
    assert "password_hash" not in payload.get("user", {})
    assert "password_hash" not in payload.get("company", {})


def test_register_user_with_initial_company(client: TestClient) -> None:
    payload = register_user(client)

    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "ana@example.com"
    assert payload["user"]["name"] == "Ana Silva"
    assert payload["company"]["name"] == "Lucro Saudável Ltda"
    assert payload["user"]["company_id"] == payload["company"]["id"]
    assert_password_hash_is_absent(payload)


def test_register_blocks_duplicate_email(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/register",
        json={
            "email": "ana@example.com",
            "password": "another-password",
            "name": "Ana Duplicada",
            "company_name": "Outra Empresa",
        },
    )

    assert response.status_code == 409
    assert_password_hash_is_absent(response.json())


def test_login_with_valid_credentials(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "password": "correct-horse-battery-staple"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["user"]["email"] == "ana@example.com"
    assert payload["company"]["name"] == "Lucro Saudável Ltda"
    assert_password_hash_is_absent(payload)


def test_login_rejects_wrong_password(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert_password_hash_is_absent(response.json())


def test_get_auth_me_with_valid_token(client: TestClient) -> None:
    registered = register_user(client)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {registered['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "ana@example.com"
    assert payload["name"] == "Ana Silva"
    assert payload["company_id"] == registered["company"]["id"]
    assert_password_hash_is_absent(payload)


def test_get_auth_me_without_token_is_unauthorized(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert_password_hash_is_absent(response.json())


def test_get_current_company_with_valid_token(client: TestClient) -> None:
    registered = register_user(client)

    response = client.get(
        "/companies/current",
        headers={"Authorization": f"Bearer {registered['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == registered["company"]["id"]
    assert payload["name"] == "Lucro Saudável Ltda"
    assert_password_hash_is_absent(payload)


def test_health_endpoint_continues_passing(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }
    assert_password_hash_is_absent(response.json())
