from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialEntry
from app.schemas.financial_summary import FinancialSummaryRead


def get_financial_summary(
    db: Session,
    company_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> FinancialSummaryRead:
    statement = select(FinancialEntry).where(FinancialEntry.company_id == company_id)

    if start_date is not None:
        statement = statement.where(FinancialEntry.entry_date >= start_date)
    if end_date is not None:
        statement = statement.where(FinancialEntry.entry_date <= end_date)

    entries = db.scalars(statement).all()
    total_revenue = sum(
        (entry.amount for entry in entries if entry.type == "revenue"), Decimal("0.00")
    )
    total_expense = sum(
        (entry.amount for entry in entries if entry.type == "expense"), Decimal("0.00")
    )
    net_result = total_revenue - total_expense

    if net_result > 0:
        summary_status = "positive"
    elif net_result < 0:
        summary_status = "negative"
    else:
        summary_status = "neutral"

    return FinancialSummaryRead(
        total_revenue=total_revenue,
        total_expense=total_expense,
        net_result=net_result,
        status=summary_status,
        entries_count=len(entries),
        start_date=start_date,
        end_date=end_date,
    )
