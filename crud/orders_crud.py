from sqlalchemy import delete, func, or_, select

from models.order_model import Order
from models.order_item_model import OrderItem
from models.order_payment_model import OrderPayment
from models.production_record_model import ProductionRecord
from models.audit_log_model import AuditLog


def get(db, order_id):
    return db.scalar(select(Order).where(Order.id == order_id).with_for_update().execution_options(populate_existing=True))


def filtered_query(filters):
    query = select(Order)
    if filters.q is not None:
        query = query.where(or_(*(column.icontains(filters.q, autoescape=True) for column in (Order.order_number, Order.customer_name, Order.customer_phone))))
    for name in ("status", "payment_status", "sales_channel", "required_date"):
        value = getattr(filters, name)
        if value is not None:
            query = query.where(getattr(Order, name) == value)
    if filters.date_from is not None:
        query = query.where(Order.order_date >= filters.date_from)
    if filters.date_to is not None:
        query = query.where(Order.order_date <= filters.date_to)
    return query


def list_orders(db, filters, order_by):
    return list(db.scalars(filtered_query(filters).order_by(order_by, Order.created_at.desc(), Order.id).limit(filters.limit).offset(filters.offset)))


def count(db, filters):
    return db.scalar(select(func.count()).select_from(filtered_query(filters).subquery()))


def items(db, order_id):
    return list(db.scalars(select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.position, OrderItem.id)))


def replace_items(db, order_id, rows):
    db.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
    db.add_all(rows)
    db.flush()


def payments(db, order_id):
    return list(db.scalars(select(OrderPayment).where(OrderPayment.order_id == order_id).order_by(OrderPayment.created_at, OrderPayment.id)))


def payment_by_key(db, order_id, key):
    return db.scalar(select(OrderPayment).where(OrderPayment.order_id == order_id, OrderPayment.payment_key == key))


def paid_amount(db, order_id):
    return db.scalar(select(func.coalesce(func.sum(OrderPayment.amount), 0)).where(OrderPayment.order_id == order_id, OrderPayment.reversed_at.is_(None)))


def production(db, order_id):
    return db.scalar(select(ProductionRecord).where(ProductionRecord.order_id == order_id))


def history(db,order_id):
    return list(db.scalars(select(AuditLog).where(AuditLog.entity_type=='order',AuditLog.entity_id==order_id).order_by(AuditLog.created_at,AuditLog.id)))


def add(db, row):
    db.add(row)
    db.flush()
    return row


def update(db, row, values):
    for key, value in values.items():
        setattr(row, key, value)
    db.flush()
