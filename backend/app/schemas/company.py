from pydantic import BaseModel


class CompanyOut(BaseModel):
    id: int
    name: str
