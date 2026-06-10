from pydantic import BaseModel, ConfigDict


class CompanyRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    email: str
    name: str
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    company_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
    company: CompanyRead
