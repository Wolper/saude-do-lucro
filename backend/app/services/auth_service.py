from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import Company, User
from app.schemas.auth import LoginRequest, RegisterRequest


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def register_user_with_company(db: Session, payload: RegisterRequest) -> tuple[User, Company, str]:
    if get_user_by_email(db, payload.email) is not None:
        raise DuplicateEmailError

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    company = Company(
        owner=user,
        name=payload.company_name,
        segment=payload.segment,
        city=payload.city or "",
        state=payload.state or "",
    )
    db.add(user)
    db.add(company)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEmailError from exc

    db.refresh(user)
    db.refresh(company)
    token = create_access_token(subject=user.id)
    return user, company, token


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError

    token = create_access_token(subject=user.id)
    return user, token
