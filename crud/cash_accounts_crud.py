from sqlalchemy import func, select
from models.cash_account_model import CashAccount


def get(db, identity, lock=False):
    query = select(CashAccount).where(CashAccount.id == identity)
    return db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)


def lock_many(db, identities):
    return list(db.scalars(select(CashAccount).where(CashAccount.id.in_(identities)).order_by(CashAccount.id).with_for_update().execution_options(populate_existing=True)))


def page(db, query):
    conditions = [] if query.is_active is None else [CashAccount.is_active == query.is_active]
    total = db.scalar(select(func.count()).select_from(CashAccount).where(*conditions))
    rows = db.scalars(select(CashAccount).where(*conditions).order_by(CashAccount.created_at, CashAccount.id).offset(query.offset).limit(query.limit))
    return list(rows), total
