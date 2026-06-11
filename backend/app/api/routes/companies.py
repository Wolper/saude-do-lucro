from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.company import CompanyOut
from app.services.auth_service import get_company_for_user

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/current", response_model=CompanyOut)
def current_company(current_user: User = Depends(get_current_user)) -> CompanyOut:
    return get_company_for_user(current_user)
