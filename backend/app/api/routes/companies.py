from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/current", response_model=CompanyRead)
def current_company(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Company:
    company = db.scalar(select(Company).where(Company.owner_id == current_user.id))
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada para o usuário autenticado.",
        )
    return company
