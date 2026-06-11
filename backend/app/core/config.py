from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Saúde do Lucro API"
    app_version: str = "0.1.0"
    service_name: str = "saude-do-lucro-api"
    token_secret: str = "saude-do-lucro-local-secret"


settings = Settings()
