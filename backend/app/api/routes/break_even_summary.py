from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.break_even_summary import BreakEvenSummaryRead
from app.services.break_even_summary_service import get_break_even_summary

router = APIRouter(prefix="/break-even-summary", tags=["break-even-summary"])


def get_current_company_id(current_user: User) -> int:
    if current_user.company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found for authenticated user",
        )
    return current_user.company.id


@router.get("", response_model=BreakEvenSummaryRead)
def read_break_even_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BreakEvenSummaryRead:
    company_id = get_current_company_id(current_user)
    return get_break_even_summary(
        db=db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
    )
