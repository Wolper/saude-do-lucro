from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import CompanyRecord, Database, UserRecord, get_db
from app.schemas import AuthResponse, CompanyRead, LoginRequest, RegisterRequest, UserRead

app = FastAPI(title="Saúde do Lucro API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "saude-do-lucro-api",
        "version": "0.1.0",
    }


@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Annotated[Database, Depends(get_db)]) -> AuthResponse:
    existing_user = db.get_user_by_email(payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user, company = db.create_user_with_company(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        company_name=payload.company_name,
    )
    return AuthResponse(access_token=create_access_token(user), user=user, company=company)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Annotated[Database, Depends(get_db)]) -> AuthResponse:
    user = db.get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    company = db.get_company_by_id(user.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return AuthResponse(access_token=create_access_token(user), user=user, company=company)


@app.get("/auth/me", response_model=UserRead)
def read_current_user(current_user: Annotated[UserRecord, Depends(get_current_user)]) -> UserRecord:
    return current_user


@app.get("/companies/current", response_model=CompanyRead)
def read_current_company(
    current_user: Annotated[UserRecord, Depends(get_current_user)],
    db: Annotated[Database, Depends(get_db)],
) -> CompanyRecord:
    company = db.get_company_by_id(current_user.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company
