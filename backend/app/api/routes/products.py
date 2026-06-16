from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.api.routes.financial_entries import get_current_company_id
from app.core.database import get_db
from app.models import Product, User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_product,
    list_products,
    list_unit_margin_ranking,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


def get_product_or_404(db: Session, product_id: int, company_id: int) -> Product:
    product = get_product(db=db, product_id=product_id, company_id=company_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return create_product(db=db, company_id=company_id, payload=payload)


@router.get("", response_model=list[ProductRead])
def list_products_endpoint(
    is_active: bool | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return list_products(db=db, company_id=company_id, is_active=is_active, category=category)


@router.get("/unit-margin-ranking", response_model=list[ProductRead])
def unit_margin_ranking(
    is_active: bool | None = True,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return list_unit_margin_ranking(
        db=db, company_id=company_id, is_active=is_active, limit=limit
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    return get_product_or_404(db=db, product_id=product_id, company_id=company_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product_endpoint(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = get_current_company_id(current_user)
    product = get_product_or_404(db=db, product_id=product_id, company_id=company_id)
    return update_product(db=db, product=product, payload=payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    company_id = get_current_company_id(current_user)
    product = get_product_or_404(db=db, product_id=product_id, company_id=company_id)
    delete_product(db=db, product=product)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
