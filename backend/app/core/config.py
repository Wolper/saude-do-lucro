from functools import lru_cache
from os import getenv


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://saude_user:saude_password@localhost:5432/saude_do_lucro"
)


class Settings:
    def __init__(self) -> None:
        self.database_url = getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
