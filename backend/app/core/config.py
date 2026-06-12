from functools import lru_cache
from os import getenv


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://saude_user:saude_password@localhost:5432/saude_do_lucro"
)


class Settings:
    def __init__(self) -> None:
        self.database_url = getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        self.jwt_secret_key = getenv("JWT_SECRET_KEY", "change-me-in-development")
        self.jwt_algorithm = getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
