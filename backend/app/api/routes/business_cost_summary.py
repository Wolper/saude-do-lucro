from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.api.routes.financial_entries import get_current_company_id
from app.core.database import get_db
from app.models import User
from app.schemas.business_cost_summary import BusinessCostSummaryRead
from app.services.business_cost_summary_service import get_business_cost_summary

router = APIRouter(prefix="/business-cost-summary", tags=["business-cost-summary"])


@router.get("", response_model=BusinessCostSummaryRead)
def read_business_cost_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BusinessCostSummaryRead:
    company_id = get_current_company_id(current_user)
    return get_business_cost_summary(db=db, company_id=company_id)
