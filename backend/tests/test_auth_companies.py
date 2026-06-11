from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Company, User  # noqa: F401


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register_payload(email: str = "joao@email.com") -> dict[str, str]:
    return {
        "name": "João",
        "email": email,
        "password": "senha_segura",
        "company_name": "MM Chicken",
        "segment": "hamburgueria",
        "city": "São Paulo",
        "state": "SP",
    }


def register_user(client: TestClient, email: str = "joao@email.com") -> dict[str, object]:
    response = client.post("/auth/register", json=register_payload(email=email))
    assert response.status_code == 201
    return response.json()


def test_register_user_with_initial_company(client: TestClient) -> None:
    data = register_user(client)

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["name"] == "João"
    assert data["user"]["email"] == "joao@email.com"
    assert "password_hash" not in data["user"]
    assert data["company"]["name"] == "MM Chicken"
    assert data["company"]["segment"] == "hamburgueria"


def test_register_blocks_duplicate_email(client: TestClient) -> None:
    register_user(client)

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "E-mail já cadastrado."


def test_login_with_valid_credentials(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login", json={"email": "joao@email.com", "password": "senha_segura"}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_fails_with_invalid_password(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login", json={"email": "joao@email.com", "password": "senha_errada"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos."


def test_auth_me_with_valid_token(client: TestClient) -> None:
    registration = register_user(client)

    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {registration['access_token']}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "joao@email.com"
    assert "password_hash" not in response.json()


def test_auth_me_without_token_is_blocked(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_current_company_with_valid_token(client: TestClient) -> None:
    registration = register_user(client)

    response = client.get(
        "/companies/current",
        headers={"Authorization": f"Bearer {registration['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "MM Chicken"
    assert response.json()["segment"] == "hamburgueria"
    assert response.json()["owner_id"] == registration["user"]["id"]
