from fastapi import FastAPI

from app.api.routes import auth, companies, health
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(companies.router)
