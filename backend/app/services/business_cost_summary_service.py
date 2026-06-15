from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BusinessCost
from app.schemas.business_cost_summary import BusinessCostSummaryRead


def get_business_cost_summary(db: Session, company_id: int) -> BusinessCostSummaryRead:
    total_active_monthly_costs_result = db.scalar(
        select(func.coalesce(func.sum(BusinessCost.amount), 0)).where(
            BusinessCost.company_id == company_id,
            BusinessCost.is_active.is_(True),
        )
    )
    active_costs_count = db.scalar(
        select(func.count())
        .select_from(BusinessCost)
        .where(
            BusinessCost.company_id == company_id,
            BusinessCost.is_active.is_(True),
        )
    )
    inactive_costs_count = db.scalar(
        select(func.count())
        .select_from(BusinessCost)
        .where(
            BusinessCost.company_id == company_id,
            BusinessCost.is_active.is_(False),
        )
    )
    total_costs_count = db.scalar(
        select(func.count())
        .select_from(BusinessCost)
        .where(BusinessCost.company_id == company_id)
    )

    active_count = int(active_costs_count or 0)

    return BusinessCostSummaryRead(
        total_active_monthly_costs=Decimal(
            str(total_active_monthly_costs_result or "0.00")
        ),
        active_costs_count=active_count,
        inactive_costs_count=int(inactive_costs_count or 0),
        total_costs_count=int(total_costs_count or 0),
        status="configured" if active_count > 0 else "empty",
    )
