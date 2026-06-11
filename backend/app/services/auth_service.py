from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.company import Company
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


def register_user_with_company(db: Session, payload: RegisterRequest) -> tuple[User, Company, str]:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        )

    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    company = Company(
        owner=user,
        name=payload.company_name,
        segment=payload.segment,
        city=payload.city,
        state=payload.state,
    )
    db.add(user)
    db.add(company)
    db.commit()
    db.refresh(user)
    db.refresh(company)

    token = create_access_token(subject=user.id)
    return user, company, token


def authenticate_user(db: Session, payload: LoginRequest) -> str:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )
    return create_access_token(subject=user.id)
