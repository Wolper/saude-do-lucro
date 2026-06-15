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


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db


def teardown_function():
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


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


def entry_payload(**overrides) -> dict:
    payload = {
        "type": "revenue",
        "category": "balcão",
        "description": "Vendas do dia",
        "amount": 100.0,
        "payment_method": "pix",
        "entry_date": "2026-06-10",
        "source": "manual",
    }
    payload.update(overrides)
    return payload


def create_entry(client: TestClient, token: str, **overrides) -> dict:
    response = client.post(
        "/financial-entries",
        json=entry_payload(**overrides),
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def get_summary(client: TestClient, token: str, query: str = "") -> dict:
    response = client.get(f"/financial-summary{query}", headers=auth_headers(token))
    assert response.status_code == 200
    return response.json()


def test_summary_without_token_is_blocked() -> None:
    response = TestClient(app).get("/financial-summary")

    assert response.status_code == 401


def test_summary_returns_zeroes_without_entries() -> None:
    client = TestClient(app)
    user = register_user(client, "zero@email.com", "Zero LTDA")

    data = get_summary(client, user["access_token"])

    assert data == {
        "total_revenue": 0.0,
        "total_expense": 0.0,
        "net_result": 0.0,
        "status": "neutral",
        "entries_count": 0,
        "start_date": None,
        "end_date": None,
    }


def test_summary_sums_revenues() -> None:
    client = TestClient(app)
    user = register_user(client, "revenues@email.com", "Receitas LTDA")
    create_entry(client, user["access_token"], type="revenue", amount=150.25)
    create_entry(client, user["access_token"], type="revenue", amount=349.75)

    data = get_summary(client, user["access_token"])

    assert data["total_revenue"] == 500.0
    assert data["total_expense"] == 0.0
    assert data["entries_count"] == 2


def test_summary_sums_expenses() -> None:
    client = TestClient(app)
    user = register_user(client, "expenses@email.com", "Despesas LTDA")
    create_entry(client, user["access_token"], type="expense", amount=120.0)
    create_entry(client, user["access_token"], type="expense", amount=80.0)

    data = get_summary(client, user["access_token"])

    assert data["total_revenue"] == 0.0
    assert data["total_expense"] == 200.0
    assert data["entries_count"] == 2


def test_summary_calculates_positive_net_result() -> None:
    client = TestClient(app)
    user = register_user(client, "positive@email.com", "Positivo LTDA")
    create_entry(client, user["access_token"], type="revenue", amount=300.0)
    create_entry(client, user["access_token"], type="expense", amount=100.0)

    data = get_summary(client, user["access_token"])

    assert data["net_result"] == 200.0
    assert data["status"] == "positive"


def test_summary_calculates_negative_net_result() -> None:
    client = TestClient(app)
    user = register_user(client, "negative@email.com", "Negativo LTDA")
    create_entry(client, user["access_token"], type="revenue", amount=50.0)
    create_entry(client, user["access_token"], type="expense", amount=100.0)

    data = get_summary(client, user["access_token"])

    assert data["net_result"] == -50.0
    assert data["status"] == "negative"


def test_summary_calculates_neutral_net_result() -> None:
    client = TestClient(app)
    user = register_user(client, "neutral@email.com", "Neutro LTDA")
    create_entry(client, user["access_token"], type="revenue", amount=100.0)
    create_entry(client, user["access_token"], type="expense", amount=100.0)

    data = get_summary(client, user["access_token"])

    assert data["net_result"] == 0.0
    assert data["status"] == "neutral"


def test_summary_applies_start_date_filter() -> None:
    client = TestClient(app)
    user = register_user(client, "start@email.com", "Start LTDA")
    create_entry(client, user["access_token"], amount=100.0, entry_date="2026-06-01")
    create_entry(client, user["access_token"], amount=200.0, entry_date="2026-06-10")

    data = get_summary(client, user["access_token"], "?start_date=2026-06-10")

    assert data["total_revenue"] == 200.0
    assert data["entries_count"] == 1
    assert data["start_date"] == "2026-06-10"
    assert data["end_date"] is None


def test_summary_applies_end_date_filter() -> None:
    client = TestClient(app)
    user = register_user(client, "end@email.com", "End LTDA")
    create_entry(client, user["access_token"], amount=100.0, entry_date="2026-06-01")
    create_entry(client, user["access_token"], amount=200.0, entry_date="2026-06-10")

    data = get_summary(client, user["access_token"], "?end_date=2026-06-01")

    assert data["total_revenue"] == 100.0
    assert data["entries_count"] == 1
    assert data["start_date"] is None
    assert data["end_date"] == "2026-06-01"


def test_summary_applies_start_and_end_date_filters() -> None:
    client = TestClient(app)
    user = register_user(client, "range@email.com", "Range LTDA")
    create_entry(client, user["access_token"], amount=100.0, entry_date="2026-06-01")
    create_entry(client, user["access_token"], amount=200.0, entry_date="2026-06-10")
    create_entry(client, user["access_token"], amount=300.0, entry_date="2026-06-30")

    data = get_summary(
        client, user["access_token"], "?start_date=2026-06-10&end_date=2026-06-30"
    )

    assert data["total_revenue"] == 500.0
    assert data["entries_count"] == 2
    assert data["start_date"] == "2026-06-10"
    assert data["end_date"] == "2026-06-30"


def test_summary_does_not_include_entries_from_another_company() -> None:
    client = TestClient(app)
    user_a = register_user(client, "a-summary@email.com", "Empresa A")
    user_b = register_user(client, "b-summary@email.com", "Empresa B")
    create_entry(client, user_a["access_token"], type="revenue", amount=100.0)
    create_entry(client, user_b["access_token"], type="revenue", amount=900.0)
    create_entry(client, user_b["access_token"], type="expense", amount=400.0)

    data = get_summary(client, user_a["access_token"])

    assert data["total_revenue"] == 100.0
    assert data["total_expense"] == 0.0
    assert data["entries_count"] == 1
