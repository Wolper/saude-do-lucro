from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import Company, User


def test_user_and_company_models_persist_relationships() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        user = User(
            name="Ana Silva",
            email="ana@example.com",
            password_hash="not-a-real-hash-yet",
        )
        company = Company(
            owner=user,
            name="Café da Ana",
            segment="cafeteria",
            city="São Paulo",
            state="SP",
        )

        session.add(user)
        session.add(company)
        session.commit()

    with Session(engine) as session:
        persisted_user = session.scalars(
            select(User).where(User.email == "ana@example.com")
        ).one()
        persisted_company = session.scalars(
            select(Company).where(Company.name == "Café da Ana")
        ).one()

        assert persisted_user.email == "ana@example.com"
        assert persisted_company.name == "Café da Ana"
        assert persisted_company.owner.email == "ana@example.com"
        assert persisted_user.company.name == "Café da Ana"
