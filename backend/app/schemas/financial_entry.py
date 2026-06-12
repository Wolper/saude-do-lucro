from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

FinancialEntryType = Literal["revenue", "expense"]


class FinancialEntryBase(BaseModel):
    type: FinancialEntryType
    category: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: str | None = Field(default=None, max_length=80)
    entry_date: date
    source: str = Field(default="manual", min_length=1, max_length=80)


class FinancialEntryCreate(FinancialEntryBase):
    pass


class FinancialEntryUpdate(BaseModel):
    type: FinancialEntryType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    payment_method: str | None = Field(default=None, max_length=80)
    entry_date: date | None = None
    source: str | None = Field(default=None, min_length=1, max_length=80)


class FinancialEntryRead(FinancialEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal) -> float:
        return float(amount)
