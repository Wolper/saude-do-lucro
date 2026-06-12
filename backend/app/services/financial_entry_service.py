from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialEntry
from app.schemas.financial_entry import FinancialEntryCreate, FinancialEntryUpdate


def create_financial_entry(
    db: Session, company_id: int, payload: FinancialEntryCreate
) -> FinancialEntry:
    entry = FinancialEntry(company_id=company_id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_financial_entries(
    db: Session,
    company_id: int,
    entry_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[FinancialEntry]:
    statement = select(FinancialEntry).where(FinancialEntry.company_id == company_id)

    if entry_type is not None:
        statement = statement.where(FinancialEntry.type == entry_type)
    if start_date is not None:
        statement = statement.where(FinancialEntry.entry_date >= start_date)
    if end_date is not None:
        statement = statement.where(FinancialEntry.entry_date <= end_date)

    statement = statement.order_by(FinancialEntry.entry_date.desc(), FinancialEntry.id.desc())
    return list(db.scalars(statement).all())


def get_financial_entry(
    db: Session, entry_id: int, company_id: int
) -> FinancialEntry | None:
    return db.scalars(
        select(FinancialEntry).where(
            FinancialEntry.id == entry_id,
            FinancialEntry.company_id == company_id,
        )
    ).first()


def update_financial_entry(
    db: Session, entry: FinancialEntry, payload: FinancialEntryUpdate
) -> FinancialEntry:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def delete_financial_entry(db: Session, entry: FinancialEntry) -> None:
    db.delete(entry)
    db.commit()
