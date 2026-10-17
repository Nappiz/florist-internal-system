from sqlalchemy import func,select
from models.supplier_store_model import SupplierStore


def get(db,identity,lock=False):
    statement=select(SupplierStore).where(SupplierStore.id==identity)
    return db.scalar(statement.with_for_update() if lock else statement)


def list_rows(db,query):
    statement=select(SupplierStore)
    if query.q: statement=statement.where(SupplierStore.name.icontains(query.q,autoescape=True))
    if query.is_active is not None: statement=statement.where(SupplierStore.is_active==query.is_active)
    if query.platform: statement=statement.where(SupplierStore.platform==query.platform)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    return list(db.scalars(statement.order_by(SupplierStore.name,SupplierStore.id).limit(query.limit).offset(query.offset))),total


def add(db,row):
    db.add(row)
    return row
