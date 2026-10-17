from sqlalchemy import func, or_, select
from models.operating_expense_model import OperatingExpense
from models.expense_payment_model import ExpensePayment
from models.expense_receipt_model import ExpenseReceipt


def get(db, identity, lock=False):
    query=select(OperatingExpense).where(OperatingExpense.id==identity)
    return db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)


def add(db, row):
    db.add(row)
    return row


def delete(db, row):
    db.delete(row)


def payment_by_key(db, key):
    return db.scalar(select(ExpensePayment).where(ExpensePayment.payment_key==key))


def paid_amount(db, identity):
    return int(db.scalar(select(func.coalesce(func.sum(ExpensePayment.amount),0)).where(ExpensePayment.expense_id==identity,ExpensePayment.reversed_at.is_(None))))


def payments(db, identity):
    return db.scalars(select(ExpensePayment).where(ExpensePayment.expense_id==identity).order_by(ExpensePayment.created_at, ExpensePayment.id)).all()


def receipts(db, identity):
    return db.scalars(select(ExpenseReceipt).where(ExpenseReceipt.expense_id==identity)).all()


def receipt(db, identity):
    return db.get(ExpenseReceipt, identity)


def filtered_query(filters, owner_id=None):
    query=select(OperatingExpense)
    if owner_id is not None:
        query=query.where(OperatingExpense.created_by==owner_id)
    if filters.search:
        pattern='%'+filters.search.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
        query=query.where(or_(OperatingExpense.title.ilike(pattern,escape='\\'),OperatingExpense.expense_number.ilike(pattern,escape='\\')))
    for field in ('category_id','status','payment_status'):
        if getattr(filters,field) is not None:
            query=query.where(getattr(OperatingExpense,field)==getattr(filters,field))
    for field, column, operation in (('date_from',OperatingExpense.expense_date,'ge'),('date_to',OperatingExpense.expense_date,'le'),('amount_min',OperatingExpense.amount,'ge'),('amount_max',OperatingExpense.amount,'le')):
        value=getattr(filters,field)
        if value is not None:
            query=query.where(column>=value if operation=='ge' else column<=value)
    return query


def list_rows(db, filters, owner_id=None, paginate=True):
    query=filtered_query(filters,owner_id).order_by(OperatingExpense.expense_date.desc(),OperatingExpense.id)
    if paginate:
        query=query.offset((filters.page-1)*filters.page_size).limit(filters.page_size)
    return db.scalars(query).all()


def count(db, filters, owner_id=None):
    return db.scalar(select(func.count()).select_from(filtered_query(filters,owner_id).subquery()))
