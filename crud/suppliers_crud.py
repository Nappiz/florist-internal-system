from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from models.supplier_model import Supplier
from schemas.supplier_schema import SupplierListQuery


def filtered_query(filters: SupplierListQuery):
    query = select(Supplier)
    if filters.q is not None:
        query = query.where(or_(
            Supplier.material_name.icontains(filters.q, autoescape=True),
            Supplier.store_name.icontains(filters.q, autoescape=True),
            Supplier.variant.icontains(filters.q, autoescape=True),
        ))
    if filters.store_name is not None:
        query = query.where(Supplier.store_name.icontains(filters.store_name, autoescape=True))
    if filters.category is not None:
        query = query.where(func.lower(Supplier.category) == filters.category.lower())
    if filters.marketplace is not None:
        query = query.where(func.lower(Supplier.marketplace) == filters.marketplace.lower())
    if filters.unit is not None:
        query = query.where(Supplier.unit == filters.unit.lower())
    if filters.min_price is not None:
        query = query.where(Supplier.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Supplier.price <= filters.max_price)
    return query


def count(db: Session, filters: SupplierListQuery) -> int:
    return db.scalar(select(func.count()).select_from(filtered_query(filters).subquery()))


def list_suppliers(db: Session, filters: SupplierListQuery, order_by) -> list[Supplier]:
    return list(db.scalars(
        filtered_query(filters)
        .order_by(order_by, Supplier.created_at.desc(), Supplier.id)
        .limit(filters.limit).offset(filters.offset)
    ))


def get_by_id(db: Session, supplier_id: UUID) -> Supplier | None:
    return db.scalar(select(Supplier).where(Supplier.id == supplier_id).with_for_update())


def add(db: Session, supplier: Supplier) -> Supplier:
    db.add(supplier)
    db.flush()
    return supplier


def update(db: Session, supplier: Supplier, values: dict) -> None:
    for field, value in values.items():
        setattr(supplier, field, value)
    db.flush()


def delete(db: Session, supplier: Supplier) -> None:
    db.delete(supplier)
    db.flush()
