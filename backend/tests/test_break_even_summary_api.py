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


def register_user(client: TestClient, email: str, company_name: str) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "name": "João",
            "email": email,
            "password": "senha_segura",
            "company_name": company_name,
            "segment": "hamburgueria",
            "city": "São Paulo",
            "state": "SP",
        },
    )
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_cost(client: TestClient, token: str, **overrides) -> dict:
    payload = {
        "name": "Aluguel",
        "category": "aluguel",
        "amount": 1000.00,
        "is_active": True,
        "notes": "Custo fixo mensal",
    }
    payload.update(overrides)
    response = client.post("/business-costs", json=payload, headers=auth_headers(token))
    assert response.status_code == 201
    return response.json()


def create_entry(client: TestClient, token: str, **overrides) -> dict:
    payload = {
        "type": "revenue",
        "category": "balcão",
        "description": "Venda",
        "amount": 100.00,
        "payment_method": "pix",
        "entry_date": "2026-06-10",
        "source": "manual",
    }
    payload.update(overrides)
    response = client.post(
        "/financial-entries", json=payload, headers=auth_headers(token)
    )
    assert response.status_code == 201
    return response.json()


def get_summary(client: TestClient, token: str, query: str = "") -> dict:
    response = client.get(f"/break-even-summary{query}", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()


def test_break_even_summary_without_token_is_blocked(client: TestClient) -> None:
    response = client.get("/break-even-summary")
    assert response.status_code == 401


def test_returns_not_configured_when_no_active_fixed_costs(client: TestClient) -> None:
    user = register_user(client, "semcustos@email.com", "Sem Custos LTDA")
    create_entry(client, user["access_token"], amount=2500.00)

    data = get_summary(client, user["access_token"])

    assert data["monthly_fixed_costs"] == 0.0
    assert data["break_even_revenue"] == 0.0
    assert data["period_revenue"] == 2500.0
    assert data["revenue_gap"] == 0.0
    assert data["coverage_percent"] is None
    assert data["status"] == "not_configured"
    assert data["active_costs_count"] == 0
    assert data["revenue_entries_count"] == 1


def test_sums_only_active_fixed_costs_and_ignores_inactive(client: TestClient) -> None:
    user = register_user(client, "custos@email.com", "Custos LTDA")
    create_cost(client, user["access_token"], amount=1200.00, is_active=True)
    create_cost(client, user["access_token"], amount=300.50, is_active=True)
    create_cost(client, user["access_token"], amount=999.99, is_active=False)

    data = get_summary(client, user["access_token"])

    assert data["monthly_fixed_costs"] == 1500.5
    assert data["break_even_revenue"] == 1500.5
    assert data["active_costs_count"] == 2


def test_sums_only_revenue_entries_and_ignores_expenses(client: TestClient) -> None:
    user = register_user(client, "receitas@email.com", "Receitas LTDA")
    create_cost(client, user["access_token"], amount=1000.00)
    create_entry(client, user["access_token"], type="revenue", amount=600.00)
    create_entry(client, user["access_token"], type="revenue", amount=150.25)
    create_entry(client, user["access_token"], type="expense", amount=700.00)

    data = get_summary(client, user["access_token"])

    assert data["period_revenue"] == 750.25
    assert data["revenue_entries_count"] == 2


def test_calculates_below_break_even_gap_and_coverage(client: TestClient) -> None:
    user = register_user(client, "abaixo@email.com", "Abaixo LTDA")
    create_cost(client, user["access_token"], amount=3700.00)
    create_entry(client, user["access_token"], amount=2500.00)

    data = get_summary(client, user["access_token"])

    assert data["status"] == "below_break_even"
    assert data["revenue_gap"] == 1200.0
    assert data["coverage_percent"] == 67.57


def test_break_even_reached_when_revenue_equals_fixed_costs(client: TestClient) -> None:
    user = register_user(client, "igual@email.com", "Igual LTDA")
    create_cost(client, user["access_token"], amount=1000.00)
    create_entry(client, user["access_token"], amount=1000.00)

    data = get_summary(client, user["access_token"])

    assert data["status"] == "break_even_reached"
    assert data["revenue_gap"] == 0.0
    assert data["coverage_percent"] == 100.0


def test_break_even_reached_when_revenue_is_greater_than_fixed_costs(client: TestClient) -> None:
    user = register_user(client, "maior@email.com", "Maior LTDA")
    create_cost(client, user["access_token"], amount=3700.00)
    create_entry(client, user["access_token"], amount=4100.00)

    data = get_summary(client, user["access_token"])

    assert data["status"] == "break_even_reached"
    assert data["revenue_gap"] == 0.0
    assert data["coverage_percent"] == 110.81


def test_applies_start_date_filter(client: TestClient) -> None:
    user = register_user(client, "inicio@email.com", "Inicio LTDA")
    create_cost(client, user["access_token"], amount=1000.00)
    create_entry(client, user["access_token"], amount=100.00, entry_date="2026-05-31")
    create_entry(client, user["access_token"], amount=300.00, entry_date="2026-06-01")

    data = get_summary(client, user["access_token"], "?start_date=2026-06-01")

    assert data["period_revenue"] == 300.0
    assert data["revenue_entries_count"] == 1
    assert data["start_date"] == "2026-06-01"


def test_applies_end_date_filter(client: TestClient) -> None:
    user = register_user(client, "fim@email.com", "Fim LTDA")
    create_cost(client, user["access_token"], amount=1000.00)
    create_entry(client, user["access_token"], amount=200.00, entry_date="2026-06-30")
    create_entry(client, user["access_token"], amount=500.00, entry_date="2026-07-01")

    data = get_summary(client, user["access_token"], "?end_date=2026-06-30")

    assert data["period_revenue"] == 200.0
    assert data["revenue_entries_count"] == 1
    assert data["end_date"] == "2026-06-30"


def test_applies_start_and_end_date_filters(client: TestClient) -> None:
    user = register_user(client, "periodo@email.com", "Periodo LTDA")
    create_cost(client, user["access_token"], amount=1000.00)
    create_entry(client, user["access_token"], amount=100.00, entry_date="2026-05-31")
    create_entry(client, user["access_token"], amount=300.00, entry_date="2026-06-15")
    create_entry(client, user["access_token"], amount=500.00, entry_date="2026-07-01")

    data = get_summary(
        client, user["access_token"], "?start_date=2026-06-01&end_date=2026-06-30"
    )

    assert data["period_revenue"] == 300.0
    assert data["revenue_entries_count"] == 1
    assert data["start_date"] == "2026-06-01"
    assert data["end_date"] == "2026-06-30"


def test_does_not_include_costs_or_revenues_from_another_company(client: TestClient) -> None:
    user_a = register_user(client, "empresa-a@email.com", "Empresa A")
    user_b = register_user(client, "empresa-b@email.com", "Empresa B")
    create_cost(client, user_a["access_token"], amount=800.00)
    create_entry(client, user_a["access_token"], amount=300.00)
    create_cost(client, user_b["access_token"], amount=9000.00)
    create_entry(client, user_b["access_token"], amount=7000.00)

    data = get_summary(client, user_a["access_token"])

    assert data["monthly_fixed_costs"] == 800.0
    assert data["period_revenue"] == 300.0
    assert data["active_costs_count"] == 1
    assert data["revenue_entries_count"] == 1
