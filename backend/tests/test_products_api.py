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


def product_payload(**overrides) -> dict:
    payload = {
        "name": "X-Burger",
        "category": "hambúrguer",
        "selling_price": 25.00,
        "estimated_unit_cost": 11.50,
        "is_active": True,
        "notes": "Produto principal",
    }
    payload.update(overrides)
    return payload


def create_product(client: TestClient, token: str, **overrides) -> dict:
    response = client.post("/products", json=product_payload(**overrides), headers=auth_headers(token))
    assert response.status_code == 201
    return response.json()


def test_create_authenticated_product(client: TestClient) -> None:
    user = register_user(client, "produto@email.com", "Produtos LTDA")
    response = client.post("/products", json=product_payload(), headers=auth_headers(user["access_token"]))
    assert response.status_code == 201
    data = response.json()
    assert data["company_id"] == user["company"]["id"]
    assert data["name"] == "X-Burger"
    assert data["category"] == "hambúrguer"
    assert data["selling_price"] == 25.0
    assert data["estimated_unit_cost"] == 11.5
    assert data["is_active"] is True
    assert data["notes"] == "Produto principal"


def test_create_without_token_is_blocked(client: TestClient) -> None:
    response = client.post("/products", json=product_payload())
    assert response.status_code == 401


@pytest.mark.parametrize("selling_price", [0, -1])
def test_create_blocks_non_positive_selling_price(client: TestClient, selling_price: int) -> None:
    user = register_user(client, f"preco{selling_price}@email.com", "Preços LTDA")
    response = client.post(
        "/products",
        json=product_payload(selling_price=selling_price),
        headers=auth_headers(user["access_token"]),
    )
    assert response.status_code == 422


def test_create_blocks_negative_estimated_unit_cost(client: TestClient) -> None:
    user = register_user(client, "custo-negativo@email.com", "Custos LTDA")
    response = client.post(
        "/products",
        json=product_payload(estimated_unit_cost=-1),
        headers=auth_headers(user["access_token"]),
    )
    assert response.status_code == 422


def test_allows_estimated_unit_cost_greater_than_selling_price(client: TestClient) -> None:
    user = register_user(client, "prejuizo@email.com", "Prejuízo LTDA")
    product = create_product(client, user["access_token"], selling_price=10, estimated_unit_cost=12)
    assert product["unit_margin"] == -2.0
    assert product["pricing_status"] == "loss"


def test_calculates_unit_margin_and_margin_percent(client: TestClient) -> None:
    user = register_user(client, "margem@email.com", "Margem LTDA")
    product = create_product(client, user["access_token"], selling_price=25, estimated_unit_cost=11.5)
    assert product["unit_margin"] == 13.5
    assert product["margin_percent"] == 54.0


@pytest.mark.parametrize(
    ("selling_price", "estimated_unit_cost", "expected"),
    [(25, 11.5, "profitable"), (25, 25, "break_even"), (10, 12, "loss")],
)
def test_pricing_status(client: TestClient, selling_price: int, estimated_unit_cost: float, expected: str) -> None:
    user = register_user(client, f"{expected}@email.com", f"{expected} LTDA")
    product = create_product(
        client, user["access_token"], selling_price=selling_price, estimated_unit_cost=estimated_unit_cost
    )
    assert product["pricing_status"] == expected


def test_list_products_from_authenticated_company(client: TestClient) -> None:
    user_a = register_user(client, "prod-a@email.com", "Empresa A")
    user_b = register_user(client, "prod-b@email.com", "Empresa B")
    product_a = create_product(client, user_a["access_token"], name="Produto A")
    create_product(client, user_b["access_token"], name="Produto B")
    response = client.get("/products", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == product_a["id"]


def test_filters_active_inactive_and_category(client: TestClient) -> None:
    user = register_user(client, "filtros-prod@email.com", "Filtros LTDA")
    create_product(client, user["access_token"], name="Ativo", category="bebida", is_active=True)
    create_product(client, user["access_token"], name="Inativo", category="bebida", is_active=False)
    create_product(client, user["access_token"], name="Pizza", category="pizza", is_active=True)
    headers = auth_headers(user["access_token"])
    assert len(client.get("/products?is_active=true", headers=headers).json()) == 2
    assert len(client.get("/products?is_active=false", headers=headers).json()) == 1
    data = client.get("/products?category=bebida", headers=headers).json()
    assert len(data) == 2
    assert {item["category"] for item in data} == {"bebida"}


def test_get_product_by_id_and_cross_company_404(client: TestClient) -> None:
    user_a = register_user(client, "consulta-prod-a@email.com", "Empresa A")
    user_b = register_user(client, "consulta-prod-b@email.com", "Empresa B")
    product_b = create_product(client, user_b["access_token"], name="Outro")
    own = create_product(client, user_a["access_token"], name="Próprio")
    response = client.get(f"/products/{own['id']}", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 200
    assert response.json()["name"] == "Próprio"
    response = client.get(f"/products/{product_b['id']}", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 404


def test_update_own_product_and_cross_company_404(client: TestClient) -> None:
    user_a = register_user(client, "update-prod-a@email.com", "Empresa A")
    user_b = register_user(client, "update-prod-b@email.com", "Empresa B")
    product_a = create_product(client, user_a["access_token"], name="Antigo")
    product_b = create_product(client, user_b["access_token"], name="Outro")
    response = client.put(
        f"/products/{product_a['id']}",
        json={"name": "Novo", "selling_price": 30},
        headers=auth_headers(user_a["access_token"]),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Novo"
    assert response.json()["unit_margin"] == 18.5
    response = client.put(
        f"/products/{product_b['id']}",
        json={"name": "Invasão"},
        headers=auth_headers(user_a["access_token"]),
    )
    assert response.status_code == 404


def test_delete_own_product_and_cross_company_404(client: TestClient) -> None:
    user_a = register_user(client, "delete-prod-a@email.com", "Empresa A")
    user_b = register_user(client, "delete-prod-b@email.com", "Empresa B")
    product_a = create_product(client, user_a["access_token"])
    product_b = create_product(client, user_b["access_token"])
    response = client.delete(f"/products/{product_a['id']}", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 204
    response = client.delete(f"/products/{product_b['id']}", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 404


def test_unit_margin_ranking_orders_by_margin_and_excludes_other_companies(client: TestClient) -> None:
    user_a = register_user(client, "ranking-prod-a@email.com", "Empresa A")
    user_b = register_user(client, "ranking-prod-b@email.com", "Empresa B")
    create_product(client, user_a["access_token"], name="Baixa", selling_price=20, estimated_unit_cost=15)
    create_product(client, user_a["access_token"], name="Alta", selling_price=40, estimated_unit_cost=10)
    create_product(client, user_a["access_token"], name="Inativa", selling_price=100, estimated_unit_cost=0, is_active=False)
    create_product(client, user_b["access_token"], name="Outra empresa", selling_price=999, estimated_unit_cost=0)
    response = client.get("/products/unit-margin-ranking", headers=auth_headers(user_a["access_token"]))
    assert response.status_code == 200
    data = response.json()
    assert [item["name"] for item in data] == ["Alta", "Baixa"]
    assert [item["unit_margin"] for item in data] == [30.0, 5.0]
    response = client.get("/products/unit-margin-ranking?is_active=false", headers=auth_headers(user_a["access_token"]))
    assert [item["name"] for item in response.json()] == ["Inativa"]
