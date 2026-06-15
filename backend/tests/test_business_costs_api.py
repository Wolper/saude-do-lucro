import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

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


def register_payload(email: str, company_name: str) -> dict[str, str]:
    return {
        "name": "João",
        "email": email,
        "password": "senha_segura",
        "company_name": company_name,
        "segment": "hamburgueria",
        "city": "São Paulo",
        "state": "SP",
    }


def register_user(client: TestClient, email: str, company_name: str) -> dict:
    response = client.post("/auth/register", json=register_payload(email, company_name))
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def cost_payload(**overrides) -> dict:
    payload = {
        "name": "Aluguel",
        "category": "aluguel",
        "amount": 2500.00,
        "is_active": True,
        "notes": "Ponto comercial",
    }
    payload.update(overrides)
    return payload


def create_cost(client: TestClient, token: str, **overrides) -> dict:
    response = client.post(
        "/business-costs",
        json=cost_payload(**overrides),
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def test_create_authenticated_business_cost(client: TestClient) -> None:
    user = register_user(client, "custo@email.com", "Custos LTDA")

    response = client.post(
        "/business-costs",
        json=cost_payload(),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["company_id"] == user["company"]["id"]
    assert data["name"] == "Aluguel"
    assert data["category"] == "aluguel"
    assert data["amount"] == 2500.0
    assert data["is_active"] is True
    assert data["notes"] == "Ponto comercial"
    assert data["created_at"]
    assert data["updated_at"]


def test_create_without_token_is_blocked(client: TestClient) -> None:
    response = client.post("/business-costs", json=cost_payload())

    assert response.status_code == 401


@pytest.mark.parametrize("amount", [0, -10])
def test_create_blocks_non_positive_amount(client: TestClient, amount: int) -> None:
    user = register_user(client, f"amount{amount}@email.com", "Amounts LTDA")

    response = client.post(
        "/business-costs",
        json=cost_payload(amount=amount),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 422


def test_list_only_authenticated_company_costs(client: TestClient) -> None:
    user_a = register_user(client, "a@email.com", "Empresa A")
    user_b = register_user(client, "b@email.com", "Empresa B")
    cost_a = create_cost(client, user_a["access_token"], name="Internet")
    create_cost(client, user_b["access_token"], name="Energia")

    response = client.get("/business-costs", headers=auth_headers(user_a["access_token"]))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == cost_a["id"]
    assert data[0]["company_id"] == user_a["company"]["id"]
    assert data[0]["name"] == "Internet"


def test_filter_active_costs(client: TestClient) -> None:
    user = register_user(client, "ativos@email.com", "Ativos LTDA")
    create_cost(client, user["access_token"], name="Aluguel", is_active=True)
    create_cost(client, user["access_token"], name="Sistema antigo", is_active=False)

    response = client.get(
        "/business-costs?is_active=true",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Aluguel"
    assert data[0]["is_active"] is True


def test_filter_inactive_costs(client: TestClient) -> None:
    user = register_user(client, "inativos@email.com", "Inativos LTDA")
    create_cost(client, user["access_token"], name="Aluguel", is_active=True)
    create_cost(client, user["access_token"], name="Sistema antigo", is_active=False)

    response = client.get(
        "/business-costs?is_active=false",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Sistema antigo"
    assert data[0]["is_active"] is False


def test_get_cost_by_id(client: TestClient) -> None:
    user = register_user(client, "consulta@email.com", "Consulta LTDA")
    cost = create_cost(client, user["access_token"], name="Contador")

    response = client.get(
        f"/business-costs/{cost['id']}", headers=auth_headers(user["access_token"])
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Contador"


def test_get_cost_from_another_company_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "ownera@email.com", "Empresa A")
    user_b = register_user(client, "ownerb@email.com", "Empresa B")
    cost_b = create_cost(client, user_b["access_token"])

    response = client.get(
        f"/business-costs/{cost_b['id']}", headers=auth_headers(user_a["access_token"])
    )

    assert response.status_code == 404


def test_update_own_company_cost(client: TestClient) -> None:
    user = register_user(client, "atualiza@email.com", "Atualiza LTDA")
    cost = create_cost(client, user["access_token"])

    response = client.put(
        f"/business-costs/{cost['id']}",
        json={"name": "Aluguel reajustado", "amount": 2750.25, "is_active": False},
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aluguel reajustado"
    assert data["amount"] == 2750.25
    assert data["is_active"] is False
    assert data["category"] == "aluguel"


def test_update_another_company_cost_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "updatea@email.com", "Empresa A")
    user_b = register_user(client, "updateb@email.com", "Empresa B")
    cost_b = create_cost(client, user_b["access_token"])

    response = client.put(
        f"/business-costs/{cost_b['id']}",
        json={"name": "Tentativa"},
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 404


def test_delete_own_company_cost(client: TestClient) -> None:
    user = register_user(client, "remove@email.com", "Remove LTDA")
    cost = create_cost(client, user["access_token"])

    response = client.delete(
        f"/business-costs/{cost['id']}", headers=auth_headers(user["access_token"])
    )

    assert response.status_code == 204
    get_response = client.get(
        f"/business-costs/{cost['id']}", headers=auth_headers(user["access_token"])
    )
    assert get_response.status_code == 404


def test_delete_another_company_cost_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "deletea@email.com", "Empresa A")
    user_b = register_user(client, "deleteb@email.com", "Empresa B")
    cost_b = create_cost(client, user_b["access_token"])

    response = client.delete(
        f"/business-costs/{cost_b['id']}", headers=auth_headers(user_a["access_token"])
    )

    assert response.status_code == 404
    get_response = client.get(
        f"/business-costs/{cost_b['id']}", headers=auth_headers(user_b["access_token"])
    )
    assert get_response.status_code == 200
