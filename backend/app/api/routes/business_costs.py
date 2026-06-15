from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.api.routes.financial_entries import get_current_company_id
from app.core.database import get_db
from app.models import User
from app.schemas.business_cost import BusinessCostCreate, BusinessCostRead, BusinessCostUpdate
from app.services.business_cost_service import (
    create_business_cost,
    delete_business_cost,
    get_business_cost,
    list_business_costs,
    update_business_cost,
)

router = APIRouter(prefix="/business-costs", tags=["business-costs"])


def get_cost_or_404(db: Session, cost_id: int, company_id: int):
    cost = get_business_cost(db=db, cost_id=cost_id, company_id=company_id)
    if cost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business cost not found",
        )
    return cost


@router.post("", response_model=BusinessCostRead, status_code=status.HTTP_201_CREATED)
def create_cost(
    payload: BusinessCostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return create_business_cost(db=db, company_id=company_id, payload=payload)


@router.get("", response_model=list[BusinessCostRead])
def list_costs(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return list_business_costs(db=db, company_id=company_id, is_active=is_active)


@router.get("/{cost_id}", response_model=BusinessCostRead)
def get_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return get_cost_or_404(db=db, cost_id=cost_id, company_id=company_id)


@router.put("/{cost_id}", response_model=BusinessCostRead)
def update_cost(
    cost_id: int,
    payload: BusinessCostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    cost = get_cost_or_404(db=db, cost_id=cost_id, company_id=company_id)
    return update_business_cost(db=db, cost=cost, payload=payload)


@router.delete("/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    company_id = get_current_company_id(current_user)
    cost = get_cost_or_404(db=db, cost_id=cost_id, company_id=company_id)
    delete_business_cost(db=db, cost=cost)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
