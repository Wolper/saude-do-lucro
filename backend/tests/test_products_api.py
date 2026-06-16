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
        "name": "Joao",
        "email": email,
        "password": "senha_segura",
        "company_name": company_name,
        "segment": "hamburgueria",
        "city": "Sao Paulo",
        "state": "SP",
    }


def register_user(client: TestClient, email: str, company_name: str) -> dict:
    response = client.post("/auth/register", json=register_payload(email, company_name))
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def product_payload(**overrides) -> dict:
    payload = {
        "name": "X Burger",
        "category": "hamburguer",
        "selling_price": 30.00,
        "estimated_unit_cost": 12.50,
        "is_active": True,
        "notes": "Produto principal",
    }
    payload.update(overrides)
    return payload


def create_product(client: TestClient, token: str, **overrides) -> dict:
    response = client.post(
        "/products",
        json=product_payload(**overrides),
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def test_create_authenticated_product(client: TestClient) -> None:
    user = register_user(client, "produto@email.com", "Produtos LTDA")

    response = client.post(
        "/products",
        json=product_payload(),
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["company_id"] == user["company"]["id"]
    assert data["name"] == "X Burger"
    assert data["category"] == "hamburguer"
    assert data["selling_price"] == 30.0
    assert data["estimated_unit_cost"] == 12.5
    assert data["unit_margin"] == 17.5
    assert data["margin_percent"] == pytest.approx(58.3333333333)
    assert data["pricing_status"] == "profitable"
    assert data["is_active"] is True
    assert data["notes"] == "Produto principal"
    assert data["created_at"]
    assert data["updated_at"]


def test_create_without_token_is_blocked(client: TestClient) -> None:
    response = client.post("/products", json=product_payload())

    assert response.status_code == 401


@pytest.mark.parametrize("selling_price", [0, -10])
def test_create_blocks_non_positive_selling_price(
    client: TestClient, selling_price: int
) -> None:
    user = register_user(client, f"preco{selling_price}@email.com", "Precos LTDA")

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


def test_list_only_authenticated_company_products(client: TestClient) -> None:
    user_a = register_user(client, "produto-a@email.com", "Empresa A")
    user_b = register_user(client, "produto-b@email.com", "Empresa B")
    product_a = create_product(client, user_a["access_token"], name="Produto A")
    create_product(client, user_b["access_token"], name="Produto B")

    response = client.get("/products", headers=auth_headers(user_a["access_token"]))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == product_a["id"]
    assert data[0]["company_id"] == user_a["company"]["id"]
    assert data[0]["name"] == "Produto A"


def test_filter_products(client: TestClient) -> None:
    user = register_user(client, "filtro-produto@email.com", "Filtros LTDA")
    create_product(client, user["access_token"], name="Ativo", category="lanche")
    create_product(
        client,
        user["access_token"],
        name="Inativo",
        category="lanche",
        is_active=False,
    )
    create_product(client, user["access_token"], name="Bebida", category="bebida")

    response = client.get(
        "/products?is_active=true&category=lanche",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Ativo"


def test_unit_margin_ranking_defaults_to_active_products(client: TestClient) -> None:
    user = register_user(client, "ranking@email.com", "Ranking LTDA")
    create_product(
        client,
        user["access_token"],
        name="Margem menor",
        selling_price=20,
        estimated_unit_cost=12,
    )
    create_product(
        client,
        user["access_token"],
        name="Margem maior",
        selling_price=50,
        estimated_unit_cost=20,
    )
    create_product(
        client,
        user["access_token"],
        name="Inativo",
        selling_price=100,
        estimated_unit_cost=1,
        is_active=False,
    )

    response = client.get(
        "/products/unit-margin-ranking", headers=auth_headers(user["access_token"])
    )

    assert response.status_code == 200
    data = response.json()
    assert [item["name"] for item in data] == ["Margem maior", "Margem menor"]
    assert data[0]["unit_margin"] == 30.0


def test_unit_margin_ranking_supports_limit_category_and_inactive(
    client: TestClient,
) -> None:
    user = register_user(client, "ranking-filtro@email.com", "Ranking Filtro LTDA")
    create_product(
        client,
        user["access_token"],
        name="Inativo bebida",
        category="bebida",
        selling_price=15,
        estimated_unit_cost=2,
        is_active=False,
    )
    create_product(
        client,
        user["access_token"],
        name="Inativo lanche",
        category="lanche",
        selling_price=30,
        estimated_unit_cost=3,
        is_active=False,
    )

    response = client.get(
        "/products/unit-margin-ranking?is_active=false&category=bebida&limit=1",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Inativo bebida"


def test_unit_margin_ranking_blocks_limit_above_max(client: TestClient) -> None:
    user = register_user(client, "ranking-limit@email.com", "Ranking Limit LTDA")

    response = client.get(
        "/products/unit-margin-ranking?limit=51",
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("selling_price", "estimated_unit_cost", "status_name"),
    [(10, 10, "break_even"), (10, 12, "loss")],
)
def test_pricing_status_values(
    client: TestClient,
    selling_price: int,
    estimated_unit_cost: int,
    status_name: str,
) -> None:
    user = register_user(client, f"status-{status_name}@email.com", "Status LTDA")

    product = create_product(
        client,
        user["access_token"],
        selling_price=selling_price,
        estimated_unit_cost=estimated_unit_cost,
    )

    assert product["pricing_status"] == status_name


def test_get_product_by_id(client: TestClient) -> None:
    user = register_user(client, "consulta-produto@email.com", "Consulta LTDA")
    product = create_product(client, user["access_token"], name="Consultar")

    response = client.get(
        f"/products/{product['id']}", headers=auth_headers(user["access_token"])
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Consultar"


def test_get_product_from_another_company_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "owner-produto-a@email.com", "Empresa A")
    user_b = register_user(client, "owner-produto-b@email.com", "Empresa B")
    product_b = create_product(client, user_b["access_token"])

    response = client.get(
        f"/products/{product_b['id']}", headers=auth_headers(user_a["access_token"])
    )

    assert response.status_code == 404


def test_update_own_company_product(client: TestClient) -> None:
    user = register_user(client, "atualiza-produto@email.com", "Atualiza LTDA")
    product = create_product(client, user["access_token"])

    response = client.put(
        f"/products/{product['id']}",
        json={"name": "X Salada", "selling_price": 35.25, "is_active": False},
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "X Salada"
    assert data["selling_price"] == 35.25
    assert data["is_active"] is False
    assert data["category"] == "hamburguer"


def test_update_another_company_product_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "update-produto-a@email.com", "Empresa A")
    user_b = register_user(client, "update-produto-b@email.com", "Empresa B")
    product_b = create_product(client, user_b["access_token"])

    response = client.put(
        f"/products/{product_b['id']}",
        json={"name": "Tentativa"},
        headers=auth_headers(user_a["access_token"]),
    )

    assert response.status_code == 404


def test_delete_own_company_product(client: TestClient) -> None:
    user = register_user(client, "remove-produto@email.com", "Remove LTDA")
    product = create_product(client, user["access_token"])

    response = client.delete(
        f"/products/{product['id']}", headers=auth_headers(user["access_token"])
    )

    assert response.status_code == 204
    get_response = client.get(
        f"/products/{product['id']}", headers=auth_headers(user["access_token"])
    )
    assert get_response.status_code == 404


def test_delete_another_company_product_returns_404(client: TestClient) -> None:
    user_a = register_user(client, "delete-produto-a@email.com", "Empresa A")
    user_b = register_user(client, "delete-produto-b@email.com", "Empresa B")
    product_b = create_product(client, user_b["access_token"])

    response = client.delete(
        f"/products/{product_b['id']}", headers=auth_headers(user_a["access_token"])
    )

    assert response.status_code == 404
    get_response = client.get(
        f"/products/{product_b['id']}", headers=auth_headers(user_b["access_token"])
    )
    assert get_response.status_code == 200
