from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, company_id: int, payload: ProductCreate) -> Product:
    product = Product(company_id=company_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(
    db: Session,
    company_id: int,
    is_active: bool | None = None,
    category: str | None = None,
) -> list[Product]:
    statement = select(Product).where(Product.company_id == company_id)
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    if category is not None:
        statement = statement.where(Product.category == category)
    statement = statement.order_by(Product.name.asc(), Product.id.asc())
    return list(db.scalars(statement).all())


def get_product(db: Session, product_id: int, company_id: int) -> Product | None:
    return db.scalars(
        select(Product).where(Product.id == product_id, Product.company_id == company_id)
    ).first()


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def list_unit_margin_ranking(
    db: Session,
    company_id: int,
    is_active: bool | None = True,
    limit: int = 10,
) -> list[Product]:
    statement = select(Product).where(Product.company_id == company_id)
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    statement = statement.order_by(
        desc(Product.selling_price - Product.estimated_unit_cost), Product.id.asc()
    ).limit(limit)
    return list(db.scalars(statement).all())
