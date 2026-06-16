from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import Company, Product, User


def test_product_model_persists_company_relationship() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        user = User(
            name="Ana Silva",
            email="ana.products@example.com",
            password_hash="not-a-real-hash-yet",
        )
        company = Company(
            owner=user,
            name="Café da Ana",
            segment="cafeteria",
            city="São Paulo",
            state="SP",
        )
        product = Product(
            company=company,
            name="Café coado",
            category="bebidas",
            selling_price=Decimal("8.50"),
            estimated_unit_cost=Decimal("2.10"),
            notes="Produto base para teste do modelo.",
        )

        session.add(product)
        session.commit()

    with Session(engine) as session:
        persisted_product = session.scalars(
            select(Product).where(Product.name == "Café coado")
        ).one()

        assert persisted_product.category == "bebidas"
        assert persisted_product.is_active is True
        assert persisted_product.company.name == "Café da Ana"
        assert persisted_product.company.products[0].name == "Café coado"
