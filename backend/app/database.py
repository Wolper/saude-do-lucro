from collections.abc import Generator
from dataclasses import dataclass
import os
import sqlite3
from typing import Protocol
from urllib.parse import urlparse

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/saude_do_lucro",
)


@dataclass(frozen=True)
class UserRecord:
    id: int
    email: str
    name: str
    password_hash: str
    company_id: int


@dataclass(frozen=True)
class CompanyRecord:
    id: int
    name: str


class Database(Protocol):
    def close(self) -> None: ...

    def create_tables(self) -> None: ...

    def get_user_by_email(self, email: str) -> UserRecord | None: ...

    def get_user_by_id(self, user_id: int) -> UserRecord | None: ...

    def get_company_by_id(self, company_id: int) -> CompanyRecord | None: ...

    def create_user_with_company(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        company_name: str,
    ) -> tuple[UserRecord, CompanyRecord]: ...


class SQLiteDatabase:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def create_tables(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                company_id INTEGER NOT NULL REFERENCES companies(id)
            )
            """
        )
        self.connection.commit()

    def get_user_by_email(self, email: str) -> UserRecord | None:
        row = self.connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return self._user_from_row(row) if row else None

    def get_user_by_id(self, user_id: int) -> UserRecord | None:
        row = self.connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._user_from_row(row) if row else None

    def get_company_by_id(self, company_id: int) -> CompanyRecord | None:
        row = self.connection.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
        return CompanyRecord(id=row["id"], name=row["name"]) if row else None

    def create_user_with_company(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        company_name: str,
    ) -> tuple[UserRecord, CompanyRecord]:
        cursor = self.connection.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
        company_id = cursor.lastrowid
        self.connection.execute(
            """
            INSERT INTO users (email, name, password_hash, company_id)
            VALUES (?, ?, ?, ?)
            """,
            (email, name, password_hash, company_id),
        )
        self.connection.commit()
        user = self.get_user_by_email(email)
        company = self.get_company_by_id(company_id)
        if user is None or company is None:
            raise RuntimeError("Failed to create user with company.")
        return user, company

    @staticmethod
    def _user_from_row(row: sqlite3.Row) -> UserRecord:
        return UserRecord(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            password_hash=row["password_hash"],
            company_id=row["company_id"],
        )


class PostgreSQLDatabase:
    def __init__(self, database_url: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self.connection = psycopg.connect(database_url, row_factory=dict_row)

    def close(self) -> None:
        self.connection.close()

    def create_tables(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    company_id INTEGER NOT NULL REFERENCES companies(id)
                )
                """
            )
        self.connection.commit()

    def get_user_by_email(self, email: str) -> UserRecord | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
        return self._user_from_row(row) if row else None

    def get_user_by_id(self, user_id: int) -> UserRecord | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
        return self._user_from_row(row) if row else None

    def get_company_by_id(self, company_id: int) -> CompanyRecord | None:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
            row = cursor.fetchone()
        return CompanyRecord(id=row["id"], name=row["name"]) if row else None

    def create_user_with_company(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        company_name: str,
    ) -> tuple[UserRecord, CompanyRecord]:
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO companies (name) VALUES (%s) RETURNING id", (company_name,))
            company_id = cursor.fetchone()["id"]
            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash, company_id)
                VALUES (%s, %s, %s, %s)
                """,
                (email, name, password_hash, company_id),
            )
        self.connection.commit()
        user = self.get_user_by_email(email)
        company = self.get_company_by_id(company_id)
        if user is None or company is None:
            raise RuntimeError("Failed to create user with company.")
        return user, company

    @staticmethod
    def _user_from_row(row: dict) -> UserRecord:
        return UserRecord(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            password_hash=row["password_hash"],
            company_id=row["company_id"],
        )


def create_sqlite_database(database_url: str = "sqlite:///:memory:") -> SQLiteDatabase:
    sqlite_path = database_url.removeprefix("sqlite:///")
    connection = sqlite3.connect(sqlite_path, check_same_thread=False)
    database = SQLiteDatabase(connection)
    database.create_tables()
    return database


def create_postgresql_database(database_url: str) -> PostgreSQLDatabase:
    database = PostgreSQLDatabase(database_url)
    database.create_tables()
    return database


def get_database() -> Database:
    scheme = urlparse(DATABASE_URL).scheme
    if scheme == "sqlite":
        return create_sqlite_database(DATABASE_URL)
    if scheme in {"postgresql", "postgres"}:
        return create_postgresql_database(DATABASE_URL)
    raise RuntimeError(f"Unsupported DATABASE_URL scheme: {scheme}")


def get_db() -> Generator[Database, None, None]:
    database = get_database()
    try:
        yield database
    finally:
        database.close()
