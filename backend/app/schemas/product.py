from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

PricingStatus = Literal["profitable", "break_even", "loss"]


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=120)
    selling_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    estimated_unit_cost: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_active: bool = True
    notes: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=120)
    selling_price: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    estimated_unit_cost: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    is_active: bool | None = None
    notes: str | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def unit_margin(self) -> Decimal:
        return self.selling_price - self.estimated_unit_cost

    @computed_field
    @property
    def margin_percent(self) -> Decimal:
        return (self.unit_margin / self.selling_price) * Decimal("100")

    @computed_field
    @property
    def pricing_status(self) -> PricingStatus:
        if self.unit_margin > 0:
            return "profitable"
        if self.unit_margin == 0:
            return "break_even"
        return "loss"

    @field_serializer("selling_price", "estimated_unit_cost", "unit_margin", "margin_percent")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)
