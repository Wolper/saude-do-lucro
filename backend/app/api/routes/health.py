from typing import TypedDict

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(TypedDict):
    status: str
    service: str
    version: str


@router.get("/health", response_model=None)
def health_check() -> HealthResponse:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.version,
    }
