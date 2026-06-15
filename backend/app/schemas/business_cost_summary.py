from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, field_serializer

BusinessCostSummaryStatus = Literal["empty", "configured"]


class BusinessCostSummaryRead(BaseModel):
    total_active_monthly_costs: Decimal
    active_costs_count: int
    inactive_costs_count: int
    total_costs_count: int
    status: BusinessCostSummaryStatus

    @field_serializer("total_active_monthly_costs")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)
