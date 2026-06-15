from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BusinessCost, FinancialEntry
from app.schemas.break_even_summary import BreakEvenSummaryRead

CENT = Decimal("0.01")
SIMPLIFIED_BREAK_EVEN_METHOD = "fixed_cost_coverage"
SIMPLIFIED_BREAK_EVEN_NOTE = (
    "Cálculo simplificado: considera apenas custos fixos ativos e receitas do período. "
    "Não considera margem por produto, custos variáveis ou CMV."
)


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def get_break_even_summary(
    db: Session,
    company_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> BreakEvenSummaryRead:
    active_costs_statement = select(
        func.coalesce(func.sum(BusinessCost.amount), 0),
        func.count(BusinessCost.id),
    ).where(
        BusinessCost.company_id == company_id,
        BusinessCost.is_active.is_(True),
    )
    monthly_fixed_costs_raw, active_costs_count = db.execute(active_costs_statement).one()
    monthly_fixed_costs = _money(Decimal(monthly_fixed_costs_raw))

    revenue_statement = select(
        func.coalesce(func.sum(FinancialEntry.amount), 0),
        func.count(FinancialEntry.id),
    ).where(
        FinancialEntry.company_id == company_id,
        FinancialEntry.type == "revenue",
    )

    if start_date is not None:
        revenue_statement = revenue_statement.where(FinancialEntry.entry_date >= start_date)
    if end_date is not None:
        revenue_statement = revenue_statement.where(FinancialEntry.entry_date <= end_date)

    period_revenue_raw, revenue_entries_count = db.execute(revenue_statement).one()
    period_revenue = _money(Decimal(period_revenue_raw))

    break_even_revenue = monthly_fixed_costs
    revenue_gap = _money(max(break_even_revenue - period_revenue, Decimal("0.00")))

    coverage_percent = None
    if break_even_revenue > 0:
        coverage_percent = ((period_revenue / break_even_revenue) * Decimal("100")).quantize(
            CENT, rounding=ROUND_HALF_UP
        )

    if monthly_fixed_costs == 0:
        status = "not_configured"
    elif period_revenue < break_even_revenue:
        status = "below_break_even"
    else:
        status = "break_even_reached"

    return BreakEvenSummaryRead(
        monthly_fixed_costs=monthly_fixed_costs,
        break_even_revenue=break_even_revenue,
        period_revenue=period_revenue,
        revenue_gap=revenue_gap,
        coverage_percent=coverage_percent,
        status=status,
        active_costs_count=active_costs_count,
        revenue_entries_count=revenue_entries_count,
        start_date=start_date,
        end_date=end_date,
        method=SIMPLIFIED_BREAK_EVEN_METHOD,
        note=SIMPLIFIED_BREAK_EVEN_NOTE,
    )
