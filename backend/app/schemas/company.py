from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyRead(BaseModel):
    id: str
    owner_id: str | None = None
    name: str
    segment: str
    city: str | None = None
    state: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CompanySummary(BaseModel):
    id: str
    name: str
    segment: str

    model_config = ConfigDict(from_attributes=True)
