from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, field_serializer

FinancialSummaryStatus = Literal["positive", "neutral", "negative"]


class FinancialSummaryRead(BaseModel):
    total_revenue: Decimal
    total_expense: Decimal
    net_result: Decimal
    status: FinancialSummaryStatus
    entries_count: int
    start_date: date | None = None
    end_date: date | None = None

    @field_serializer("total_revenue", "total_expense", "net_result")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)
