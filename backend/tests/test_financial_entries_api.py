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


def entry_payload(**overrides) -> dict:
    payload = {
        "type": "revenue",
        "category": "balcão",
        "description": "Vendas do dia",
        "amount": 850.50,
        "payment_method": "pix",
        "entry_date": "2026-06-09",
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


def test_create_authenticated_revenue(client: TestClient) -> None:
    user = register_user(client, "receita@email.com", "Receitas LTDA")

    response = client.post(
        "/financial-entries",
        json=entry_payload(),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["company_id"] == user["company"]["id"]
    assert data["type"] == "revenue"
    assert data["category"] == "balcão"
    assert data["description"] == "Vendas do dia"
    assert data["amount"] == 850.50
    assert data["payment_method"] == "pix"
    assert data["entry_date"] == "2026-06-09"
    assert data["source"] == "manual"
    assert data["created_at"]


def test_create_authenticated_expense(client: TestClient) -> None:
    user = register_user(client, "despesa@email.com", "Despesas LTDA")

    response = client.post(
        "/financial-entries",
        json=entry_payload(
            type="expense",
            category="aluguel",
            description="Aluguel do mês",
            amount=1200,
            payment_method="boleto",
        ),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "expense"
    assert data["category"] == "aluguel"
    assert data["amount"] == 1200.0


def test_create_without_token_is_blocked(client: TestClient) -> None:
    response = client.post("/financial-entries", json=entry_payload())

    assert response.status_code == 401


@pytest.mark.parametrize("amount", [0, -10])
def test_create_blocks_non_positive_amount(client: TestClient, amount: int) -> None:
    user = register_user(client, f"amount{amount}@email.com", "Amounts LTDA")

    response = client.post(
        "/financial-entries",
        json=entry_payload(amount=amount),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 422


def test_create_blocks_invalid_type(client: TestClient) -> None:
    user = register_user(client, "tipo@email.com", "Tipos LTDA")

    response = client.post(
        "/financial-entries",
        json=entry_payload(type="transfer"),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 422


def test_list_only_authenticated_company_entries(client: TestClient) -> None:
    user_a = register_user(client, "a@email.com", "Empresa A")
    user_b = register_user(client, "b@email.com", "Empresa B")
    entry_a = create_entry(client, user_a["access_token"], description="Da empresa A")
    create_entry(client, user_b["access_token"], description="Da empresa B")

    response = client.get(
        "/financial-entries",
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == entry_a["id"]
    assert data[0]["company_id"] == user_a["company"]["id"]
    assert data[0]["description"] == "Da empresa A"


def test_list_applies_simple_filters(client: TestClient) -> None:
    user = register_user(client, "filtros@email.com", "Filtros LTDA")
    create_entry(client, user["access_token"], type="revenue", entry_date="2026-06-09")
    create_entry(client, user["access_token"], type="expense", entry_date="2026-06-10")
    create_entry(client, user["access_token"], type="expense", entry_date="2026-06-15")

    response = client.get(
        "/financial-entries?type=expense&start_date=2026-06-10&end_date=2026-06-10",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "expense"
    assert data[0]["entry_date"] == "2026-06-10"


def test_get_entry_by_id(client: TestClient) -> None:
    user = register_user(client, "consulta@email.com", "Consulta LTDA")
    entry = create_entry(client, user["access_token"], description="Consultar")

    response = client.get(
        f"/financial-entries/{entry['id']}",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Consultar"


def test_get_entry_from_another_company_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "ownera@email.com", "Empresa A")
    user_b = register_user(client, "ownerb@email.com", "Empresa B")
    entry_b = create_entry(client, user_b["access_token"])

    response = client.get(
        f"/financial-entries/{entry_b['id']}",
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 404


def test_update_own_company_entry(client: TestClient) -> None:
    user = register_user(client, "atualiza@email.com", "Atualiza LTDA")
    entry = create_entry(client, user["access_token"])

    response = client.put(
        f"/financial-entries/{entry['id']}",
        json={"category": "delivery", "amount": 990.75},
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "delivery"
    assert data["amount"] == 990.75
    assert data["description"] == "Vendas do dia"


def test_update_another_company_entry_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "updatea@email.com", "Empresa A")
    user_b = register_user(client, "updateb@email.com", "Empresa B")
    entry_b = create_entry(client, user_b["access_token"])

    response = client.put(
        f"/financial-entries/{entry_b['id']}",
        json={"category": "delivery"},
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 404


def test_delete_own_company_entry(client: TestClient) -> None:
    user = register_user(client, "remove@email.com", "Remove LTDA")
    entry = create_entry(client, user["access_token"])

    response = client.delete(
        f"/financial-entries/{entry['id']}",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 204
    get_response = client.get(
        f"/financial-entries/{entry['id']}",
        headers=auth_headers(user["access_token"]),
    )
    assert get_response.status_code == 404


def test_delete_another_company_entry_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "deletea@email.com", "Empresa A")
    user_b = register_user(client, "deleteb@email.com", "Empresa B")
    entry_b = create_entry(client, user_b["access_token"])

    response = client.delete(
        f"/financial-entries/{entry_b['id']}",
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 404
    get_response = client.get(
        f"/financial-entries/{entry_b['id']}",
        headers=auth_headers(user_b["access_token"]),
    )
    assert get_response.status_code == 200
