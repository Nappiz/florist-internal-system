from sqlalchemy import and_, case, func, literal, or_, select, union_all
from sqlalchemy.orm import aliased
from models.cash_operation_model import CashOperation
from models.cash_transaction_model import CashTransaction as T
from models.cash_account_model import CashAccount


def operation(db, key):
    return db.get(CashOperation, key)


def get(db, identity, lock=False):
    query = select(T).where(T.id == identity)
    return db.scalar(query.with_for_update() if lock else query)


def by_source(db, source_type, source_id):
    return db.scalar(select(T).where(T.source_type == source_type, T.source_id == source_id))


def reversal(db, identity):
    return db.scalar(select(T).where(T.reversal_of_id == identity))


def by_operation(db, key):
    return list(db.scalars(select(T).where(T.operation_key == key).order_by(T.created_at, T.id)))


def balance(db, account_id):
    return int(db.scalar(select(func.coalesce(func.sum(case((T.direction == 'IN', T.amount), else_=-T.amount)), 0)).where(T.cash_account_id == account_id)))


def filters(query, table=T, dates=True):
    conditions = []
    for key in ('cash_account_id', 'source_type', 'category', 'direction'):
        value = getattr(query, key, None)
        if value is not None:
            conditions.append(getattr(table.c if hasattr(table, 'c') else table, key) == value)
    columns = table.c if hasattr(table, 'c') else table
    if dates and query.date_from is not None:
        conditions.append(columns.transaction_date >= query.date_from)
    if dates and query.date_to is not None:
        conditions.append(columns.transaction_date <= query.date_to)
    return conditions


def totals(db, query):
    conditions = filters(query, dates=False)
    if query.cash_account_id is None:
        conditions.append(T.source_type != 'transfer')
    before = T.transaction_date < query.date_from if query.date_from else literal(False)
    within = and_(T.transaction_date >= query.date_from if query.date_from else literal(True), T.transaction_date <= query.date_to if query.date_to else literal(True))
    signed = case((T.direction == 'IN', T.amount), else_=-T.amount)
    return db.execute(select(
        func.coalesce(func.sum(case((before, signed), else_=0)), 0),
        func.coalesce(func.sum(case((and_(within, T.direction == 'IN'), T.amount), else_=0)), 0),
        func.coalesce(func.sum(case((and_(within, T.direction == 'OUT'), T.amount), else_=0)), 0),
    ).where(*conditions)).one()


def ledger_query(query):
    running = func.sum(case((T.direction == 'IN', T.amount), else_=-T.amount)).over(partition_by=T.cash_account_id, order_by=(T.transaction_date, T.created_at, T.id), rows=(None, 0)).label('running_balance')
    ledger = select(T, CashAccount.name.label('account_name'), running).join(CashAccount, CashAccount.id == T.cash_account_id).subquery()
    conditions = filters(query, ledger)
    return select(ledger).where(*conditions).order_by(ledger.c.transaction_date, ledger.c.created_at, ledger.c.id)


def history(db, query):
    statement = ledger_query(query)
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery()))
    rows = db.execute(statement.offset(query.offset).limit(query.limit)).mappings().all()
    return [dict(row) for row in rows], total


def export_rows(db, query):
    return db.execute(ledger_query(query).execution_options(stream_results=True, yield_per=500)).mappings()


def breakdown(db, query):
    conditions = filters(query)
    if query.cash_account_id is None:
        conditions.append(T.source_type != 'transfer')
    return [dict(row) for row in db.execute(select(T.category, T.direction, func.sum(T.amount).label('amount')).where(*conditions).group_by(T.category, T.direction).order_by(T.category, T.direction)).mappings()]


def payment_model(source_type):
    from models.order_payment_model import OrderPayment
    from models.purchase_payment_model import PurchasePayment
    from models.expense_payment_model import ExpensePayment
    return {'order_payment': OrderPayment, 'purchase_payment': PurchasePayment, 'expense_payment': ExpensePayment}[source_type]


def parent_model(source_type):
    from models.order_model import Order
    from models.purchase_model import Purchase
    from models.operating_expense_model import OperatingExpense
    return {'order_payment': (Order, 'order_id'), 'purchase_payment': (Purchase, 'purchase_id'), 'expense_payment': (OperatingExpense, 'expense_id')}[source_type]


def source_payment(db, source_type, identity, lock=False):
    model = payment_model(source_type)
    query = select(model).where(model.id == identity)
    return db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)


def lock_parent(db, source_type, payment):
    model, column = parent_model(source_type)
    return db.scalar(select(model).where(model.id == getattr(payment, column)).with_for_update().execution_options(populate_existing=True))


def paid_amount(db, source_type, payment):
    model = payment_model(source_type)
    _, column = parent_model(source_type)
    return int(db.scalar(select(func.coalesce(func.sum(model.amount), 0)).where(getattr(model, column) == getattr(payment, column), model.reversed_at.is_(None))))


def expense_category(db, expense_id):
    from models.operating_expense_model import OperatingExpense
    from models.expense_category_model import ExpenseCategory
    return db.scalar(select(ExpenseCategory.name).join(OperatingExpense, OperatingExpense.category_id == ExpenseCategory.id).where(OperatingExpense.id == expense_id))


def reconciliation(db, limit, offset):
    queries = []
    reverse = aliased(T)
    duplicates = select(T.source_type, T.source_id, func.count().label('count')).group_by(T.source_type, T.source_id).subquery()
    for source_type in ('order_payment', 'purchase_payment', 'expense_payment'):
        payment = payment_model(source_type)
        issue = case(
            (payment.cash_account_id.is_(None), 'unmapped_payment'),
            (T.id.is_(None), 'missing_ledger'),
            (duplicates.c.count > 1, 'duplicate_ledger'),
            (T.amount != payment.amount, 'amount_mismatch'),
            (T.cash_account_id != payment.cash_account_id, 'account_mismatch'),
            (T.transaction_date != payment.payment_date, 'date_mismatch'),
            (T.direction != ('IN' if source_type == 'order_payment' else 'OUT'), 'direction_mismatch'),
            (or_(and_(payment.reversed_at.is_not(None), reverse.id.is_(None)), and_(payment.reversed_at.is_(None), reverse.id.is_not(None)), and_(reverse.id.is_not(None), or_(reverse.amount != T.amount, reverse.cash_account_id != T.cash_account_id, reverse.direction == T.direction))), 'reversal_mismatch'),
            else_=None,
        ).label('issue')
        query = select(literal(source_type).label('source_type'), payment.id.label('payment_id'), T.id.label('transaction_id'), issue).select_from(payment).outerjoin(T, and_(T.source_type == source_type, T.source_id == payment.id)).outerjoin(duplicates, and_(duplicates.c.source_type == source_type, duplicates.c.source_id == payment.id)).outerjoin(reverse, reverse.reversal_of_id == T.id)
        queries.append(query)
        queries.append(select(literal(source_type).label('source_type'), T.source_id.label('payment_id'), T.id.label('transaction_id'), literal('orphan_ledger').label('issue')).select_from(T).outerjoin(payment, payment.id == T.source_id).where(T.source_type == source_type, payment.id.is_(None)))
    joined = union_all(*queries).subquery()
    condition = joined.c.issue.is_not(None)
    total = db.scalar(select(func.count()).select_from(joined).where(condition))
    counts = dict(db.execute(select(joined.c.issue, func.count()).where(condition).group_by(joined.c.issue)).all())
    rows = db.execute(select(joined).where(condition).order_by(joined.c.source_type, joined.c.payment_id).limit(limit).offset(offset)).mappings()
    return [dict(row) for row in rows], total, counts
