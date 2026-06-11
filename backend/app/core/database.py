from app.models.company import Company
from app.models.user import User


class InMemoryDatabase:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.users: dict[int, User] = {}
        self.companies: dict[int, Company] = {}
        self._next_user_id = 1
        self._next_company_id = 1

    def create_company(self, name: str) -> Company:
        company = Company(id=self._next_company_id, name=name)
        self.companies[company.id] = company
        self._next_company_id += 1
        return company

    def create_user(self, email: str, hashed_password: str, company_id: int) -> User:
        user = User(
            id=self._next_user_id,
            email=email.lower(),
            hashed_password=hashed_password,
            company_id=company_id,
        )
        self.users[user.id] = user
        self._next_user_id += 1
        return user

    def get_user_by_email(self, email: str) -> User | None:
        normalized_email = email.lower()
        return next((user for user in self.users.values() if user.email == normalized_email), None)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def get_company_by_id(self, company_id: int) -> Company | None:
        return self.companies.get(company_id)


database = InMemoryDatabase()


def reset_database() -> None:
    database.reset()
