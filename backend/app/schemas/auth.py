from pydantic import BaseModel, Field, model_validator

from app.schemas.company import CompanyOut
from app.schemas.user import UserOut


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    company_name: str | None = None
    name: str | None = None

    @model_validator(mode="after")
    def require_company_name(self) -> "RegisterRequest":
        if not (self.company_name or self.name):
            raise ValueError("company_name is required")
        return self

    @property
    def normalized_company_name(self) -> str:
        return (self.company_name or self.name or "").strip()


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    company: CompanyOut
