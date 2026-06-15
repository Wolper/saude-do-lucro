from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BusinessCost
from app.schemas.business_cost import BusinessCostCreate, BusinessCostUpdate


def create_business_cost(db: Session, company_id: int, payload: BusinessCostCreate) -> BusinessCost:
    cost = BusinessCost(company_id=company_id, **payload.model_dump())
    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


def list_business_costs(
    db: Session, company_id: int, is_active: bool | None = None
) -> list[BusinessCost]:
    statement = select(BusinessCost).where(BusinessCost.company_id == company_id)

    if is_active is not None:
        statement = statement.where(BusinessCost.is_active == is_active)

    statement = statement.order_by(BusinessCost.id.desc())
    return list(db.scalars(statement).all())


def get_business_cost(db: Session, cost_id: int, company_id: int) -> BusinessCost | None:
    return db.scalars(
        select(BusinessCost).where(
            BusinessCost.id == cost_id,
            BusinessCost.company_id == company_id,
        )
    ).first()


def update_business_cost(
    db: Session, cost: BusinessCost, payload: BusinessCostUpdate
) -> BusinessCost:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cost, field, value)

    db.add(cost)
    db.commit()
    db.refresh(cost)
    return cost


def delete_business_cost(db: Session, cost: BusinessCost) -> None:
    db.delete(cost)
    db.commit()
