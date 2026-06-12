from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.financial_entry import (
    FinancialEntryCreate,
    FinancialEntryRead,
    FinancialEntryUpdate,
)
from app.services.financial_entry_service import (
    create_financial_entry,
    delete_financial_entry,
    get_financial_entry,
    list_financial_entries,
    update_financial_entry,
)

router = APIRouter(prefix="/financial-entries", tags=["financial-entries"])


def get_current_company_id(current_user: User) -> int:
    if current_user.company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found for authenticated user",
        )
    return current_user.company.id


def get_entry_or_404(db: Session, entry_id: int, company_id: int):
    entry = get_financial_entry(db=db, entry_id=entry_id, company_id=company_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial entry not found",
        )
    return entry


@router.post("", response_model=FinancialEntryRead, status_code=status.HTTP_201_CREATED)
def create_entry(
    payload: FinancialEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return create_financial_entry(db=db, company_id=company_id, payload=payload)


@router.get("", response_model=list[FinancialEntryRead])
def list_entries(
    type: Literal["revenue", "expense"] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return list_financial_entries(
        db=db,
        company_id=company_id,
        entry_type=type,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{entry_id}", response_model=FinancialEntryRead)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return get_entry_or_404(db=db, entry_id=entry_id, company_id=company_id)


@router.put("/{entry_id}", response_model=FinancialEntryRead)
def update_entry(
    entry_id: int,
    payload: FinancialEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    entry = get_entry_or_404(db=db, entry_id=entry_id, company_id=company_id)
    return update_financial_entry(db=db, entry=entry, payload=payload)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    company_id = get_current_company_id(current_user)
    entry = get_entry_or_404(db=db, entry_id=entry_id, company_id=company_id)
    delete_financial_entry(db=db, entry=entry)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
