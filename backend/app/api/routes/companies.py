from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth import get_current_user
from app.models import User
from app.schemas.company import CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/current", response_model=CompanyRead)
def current_company(current_user: User = Depends(get_current_user)):
    if current_user.company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found for authenticated user",
        )

    return current_user.company
