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


def test_summary_without_token_is_blocked(client: TestClient) -> None:
    response = client.get("/business-cost-summary")

    assert response.status_code == 401


def test_summary_returns_zero_when_company_has_no_costs(client: TestClient) -> None:
    user = register_user(client, "semcustos@email.com", "Sem Custos LTDA")

    response = client.get(
        "/business-cost-summary",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_active_monthly_costs": 0.0,
        "active_costs_count": 0,
        "inactive_costs_count": 0,
        "total_costs_count": 0,
        "status": "empty",
    }


def test_summary_sums_only_active_costs_and_counts_all_statuses(
    client: TestClient,
) -> None:
    user = register_user(client, "resumo@email.com", "Resumo LTDA")
    create_cost(
        client, user["access_token"], name="Aluguel", amount=2500.00, is_active=True
    )
    create_cost(
        client, user["access_token"], name="Internet", amount=200.50, is_active=True
    )
    create_cost(
        client,
        user["access_token"],
        name="Sistema antigo",
        amount=999.99,
        is_active=False,
    )

    response = client.get(
        "/business-cost-summary",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_active_monthly_costs"] == 2700.5
    assert data["active_costs_count"] == 2
    assert data["inactive_costs_count"] == 1
    assert data["total_costs_count"] == 3
    assert data["status"] == "configured"


def test_summary_inactive_costs_do_not_enter_active_total(client: TestClient) -> None:
    user = register_user(client, "inativos-total@email.com", "Inativos Total LTDA")
    create_cost(
        client, user["access_token"], name="Ativo", amount=100.00, is_active=True
    )
    create_cost(
        client, user["access_token"], name="Inativo", amount=900.00, is_active=False
    )

    response = client.get(
        "/business-cost-summary",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["total_active_monthly_costs"] == 100.0


def test_summary_returns_empty_when_company_has_only_inactive_costs(
    client: TestClient,
) -> None:
    user = register_user(client, "soinativos@email.com", "Só Inativos LTDA")
    create_cost(
        client, user["access_token"], name="Inativo A", amount=100.00, is_active=False
    )
    create_cost(
        client, user["access_token"], name="Inativo B", amount=200.00, is_active=False
    )

    response = client.get(
        "/business-cost-summary",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_active_monthly_costs": 0.0,
        "active_costs_count": 0,
        "inactive_costs_count": 2,
        "total_costs_count": 2,
        "status": "empty",
    }


def test_summary_does_not_include_costs_from_another_company(
    client: TestClient,
) -> None:
    user_a = register_user(client, "empresa-a@email.com", "Empresa A")
    user_b = register_user(client, "empresa-b@email.com", "Empresa B")
    create_cost(
        client, user_a["access_token"], name="A ativo", amount=300.00, is_active=True
    )
    create_cost(
        client, user_b["access_token"], name="B ativo", amount=700.00, is_active=True
    )
    create_cost(
        client, user_b["access_token"], name="B inativo", amount=900.00, is_active=False
    )

    response = client.get(
        "/business-cost-summary",
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_active_monthly_costs": 300.0,
        "active_costs_count": 1,
        "inactive_costs_count": 0,
        "total_costs_count": 1,
        "status": "configured",
    }
