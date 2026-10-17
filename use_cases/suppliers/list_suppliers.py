from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import suppliers_crud
from models.supplier_model import Supplier
from schemas.supplier_schema import SupplierListQuery, SupplierPage
from use_cases.suppliers.supplier_response import supplier_response


def list_suppliers(db: Session, filters: SupplierListQuery) -> SupplierPage:
    if filters.min_price is not None and filters.max_price is not None and filters.min_price > filters.max_price:
        raise HTTPException(422, "min_price tidak boleh melebihi max_price.")
    order = {
        "newest": Supplier.created_at.desc(),
        "price_asc": Supplier.price.asc(),
        "price_desc": Supplier.price.desc(),
        "unit_price_asc": (Supplier.price / Supplier.pack_quantity).asc(),
    }[filters.sort]
    total = suppliers_crud.count(db, filters)
    records = suppliers_crud.list_suppliers(db, filters, order)
    return SupplierPage(items=[supplier_response(record) for record in records], total=total, limit=filters.limit, offset=filters.offset)
