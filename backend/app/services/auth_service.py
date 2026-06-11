from fastapi import HTTPException, status

from app.core.database import database
from app.core.security import create_access_token, hash_password, verify_password
from app.models.company import Company
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.company import CompanyOut
from app.schemas.user import UserOut


def build_user_out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, company_id=user.company_id)


def build_company_out(company: Company) -> CompanyOut:
    return CompanyOut(id=company.id, name=company.name)


def build_auth_response(user: User, company: Company) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=build_user_out(user),
        company=build_company_out(company),
    )


def register_user(payload: RegisterRequest) -> AuthResponse:
    if database.get_user_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered",
        )

    company = database.create_company(payload.normalized_company_name)
    user = database.create_user(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        company_id=company.id,
    )
    return build_auth_response(user, company)


def authenticate_user(payload: LoginRequest) -> AuthResponse:
    user = database.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    company = database.get_company_by_id(user.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return build_auth_response(user, company)


def get_company_for_user(user: User) -> CompanyOut:
    company = database.get_company_by_id(user.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return build_company_out(company)
