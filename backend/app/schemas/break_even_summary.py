from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, field_serializer

BreakEvenStatus = Literal["not_configured", "below_break_even", "break_even_reached"]


class BreakEvenSummaryRead(BaseModel):
    monthly_fixed_costs: Decimal
    break_even_revenue: Decimal
    period_revenue: Decimal
    revenue_gap: Decimal
    coverage_percent: Decimal | None
    status: BreakEvenStatus
    active_costs_count: int
    revenue_entries_count: int
    start_date: date | None = None
    end_date: date | None = None
    method: Literal["fixed_cost_coverage"] = "fixed_cost_coverage"
    note: str = (
        "Cálculo simplificado: considera apenas custos fixos ativos e receitas do "
        "período. Não considera margem por produto, custos variáveis ou CMV."
    )

    @field_serializer(
        "monthly_fixed_costs",
        "break_even_revenue",
        "period_revenue",
        "revenue_gap",
        "coverage_percent",
    )
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        if value is None:
            return None
        return float(value)
