import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Company, User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


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


def register_user(client: TestClient, email: str = "joao@email.com") -> dict:
    response = client.post("/auth/register", json=register_payload(email=email))
    assert response.status_code == 201
    return response.json()


def test_register_user_with_initial_company(client: TestClient) -> None:
    data = register_user(client)

    assert data["user"] == {"id": 1, "name": "João", "email": "joao@email.com"}
    assert data["company"] == {
        "id": 1,
        "name": "MM Chicken",
        "segment": "hamburgueria",
    }

    with Session(engine) as session:
        user = session.scalars(select(User).where(User.email == "joao@email.com")).one()
        company = session.scalars(select(Company).where(Company.owner_id == user.id)).one()

        assert user.password_hash != "senha_segura"
        assert company.owner_id == user.id
        assert user.company.name == "MM Chicken"


def test_register_response_contains_access_token_user_and_company(client: TestClient) -> None:
    data = register_user(client)

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "joao@email.com"
    assert data["company"]["name"] == "MM Chicken"


def test_register_response_does_not_contain_password_hash(client: TestClient) -> None:
    data = register_user(client)

    assert "password_hash" not in data
    assert "password_hash" not in data["user"]
    assert "password" not in data["user"]


def test_duplicate_email_is_blocked(client: TestClient) -> None:
    register_user(client)

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code in {400, 409}


def test_login_with_correct_credentials_returns_token(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "joao@email.com", "password": "senha_segura"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "joao@email.com", "password": "senha_errada"},
    )

    assert response.status_code == 401


def test_auth_me_with_valid_token_returns_user(client: TestClient) -> None:
    data = register_user(client)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "João", "email": "joao@email.com"}


def test_auth_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


def test_current_company_with_valid_token_returns_company(client: TestClient) -> None:
    data = register_user(client)

    response = client.get(
        "/companies/current",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "MM Chicken",
        "segment": "hamburgueria",
    }
