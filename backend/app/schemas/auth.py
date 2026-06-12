from pydantic import BaseModel, EmailStr, Field

from app.schemas.company import CompanyRead
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    company_name: str = Field(min_length=1)
    segment: str = Field(min_length=1)
    city: str = ""
    state: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(TokenResponse):
    user: UserRead
    company: CompanyRead
