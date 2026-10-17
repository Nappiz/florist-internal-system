from sqlalchemy import delete,func,or_,select
from models.purchase_model import Purchase
from models.purchase_item_model import PurchaseItem
from models.purchase_payment_model import PurchasePayment


def get(db,identity,lock=False):
    statement=select(Purchase).where(Purchase.id==identity)
    return db.scalar(statement.with_for_update() if lock else statement)


def items(db,identity):
    return list(db.scalars(select(PurchaseItem).where(PurchaseItem.purchase_id==identity).order_by(PurchaseItem.id)))


def list_item_names(db,identities):
    statement=select(PurchaseItem.purchase_id,PurchaseItem.material_name_snapshot).where(PurchaseItem.purchase_id.in_(identities)).order_by(PurchaseItem.purchase_id,PurchaseItem.id)
    return db.execute(statement).all()


def payments(db,identity):
    return list(db.scalars(select(PurchasePayment).where(PurchasePayment.purchase_id==identity).order_by(PurchasePayment.created_at,PurchasePayment.id)))


def clear_items(db,identity):
    db.execute(delete(PurchaseItem).where(PurchaseItem.purchase_id==identity))


def list_rows(db,query):
    statement=select(Purchase)
    if query.q: statement=statement.where(or_(Purchase.purchase_number.icontains(query.q,autoescape=True),Purchase.reference_number.icontains(query.q,autoescape=True)))
    if query.supplier_id: statement=statement.where(Purchase.supplier_id==query.supplier_id)
    if query.status: statement=statement.where(Purchase.status==query.status)
    if query.payment_status: statement=statement.where(Purchase.payment_status==query.payment_status)
    if query.date_from: statement=statement.where(Purchase.purchase_date>=query.date_from)
    if query.date_to: statement=statement.where(Purchase.purchase_date<=query.date_to)
    if query.min_total is not None: statement=statement.where(Purchase.total_amount>=query.min_total)
    if query.max_total is not None: statement=statement.where(Purchase.total_amount<=query.max_total)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    return list(db.scalars(statement.order_by(Purchase.created_at.desc(),Purchase.id).limit(query.limit).offset(query.offset))),total
