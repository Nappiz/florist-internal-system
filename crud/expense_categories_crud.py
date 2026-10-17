from sqlalchemy import select, func
from models.expense_category_model import ExpenseCategory


def get(db, identity, lock=False):
    query=select(ExpenseCategory).where(ExpenseCategory.id==identity)
    return db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)


def list_rows(db):
    return db.scalars(select(ExpenseCategory).order_by(ExpenseCategory.name)).all()


def page(db, filters, active_only=False):
    query=select(ExpenseCategory)
    if active_only:
        query=query.where(ExpenseCategory.is_active.is_(True))
    elif filters.is_active is not None:
        query=query.where(ExpenseCategory.is_active==filters.is_active)
    if filters.q:
        query=query.where(ExpenseCategory.name.ilike('%'+filters.q.replace('%','\\%').replace('_','\\_')+'%',escape='\\'))
    count=db.scalar(select(func.count()).select_from(query.subquery()))
    rows=db.scalars(query.order_by(ExpenseCategory.name,ExpenseCategory.id).limit(filters.limit).offset(filters.offset)).all()
    return rows,count


def add(db, row):
    db.add(row)
    return row
