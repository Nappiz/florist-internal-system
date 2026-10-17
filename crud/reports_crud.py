from sqlalchemy import func, select

from models.inventory_balance_model import InventoryBalance
from models.inventory_movement_model import InventoryMovement
from models.material_model import Material
from models.order_model import Order
from models.order_item_model import OrderItem
from models.order_payment_model import OrderPayment
from models.product_model import Product
from models.production_record_model import ProductionRecord
from models.purchase_model import Purchase
from models.purchase_item_model import PurchaseItem
from models.supplier_store_model import SupplierStore


def received_purchases(db, date_from, date_to):
    return db.execute(select(Purchase, SupplierStore.name).join(SupplierStore, Purchase.supplier_id == SupplierStore.id)
        .where(Purchase.status == "received", Purchase.purchase_date.between(date_from, date_to))).all()


def received_purchase_items(db, date_from, date_to):
    return db.scalars(select(PurchaseItem).join(Purchase, Purchase.id == PurchaseItem.purchase_id)
        .where(Purchase.status == "received", Purchase.purchase_date.between(date_from, date_to))).all()


def completed_orders(db, start, end):
    return db.scalars(select(Order).where(Order.status == "completed", Order.completed_at >= start, Order.completed_at < end)).all()


def completed_items(db, start, end):
    return db.scalars(select(OrderItem).join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == "completed", Order.completed_at >= start, Order.completed_at < end)).all()


def payments(db, date_from, date_to):
    return db.execute(select(OrderPayment, Order.status).join(Order, Order.id == OrderPayment.order_id)
        .where(OrderPayment.payment_date.between(date_from, date_to), OrderPayment.reversed_at.is_(None))).all()


def order_status_counts(db, date_from, date_to):
    return db.execute(select(Order.status, func.count()).where(Order.order_date.between(date_from, date_to)).group_by(Order.status)).all()


def purchase_status_counts(db, date_from, date_to):
    return db.execute(select(Purchase.status, func.count()).where(Purchase.purchase_date.between(date_from, date_to)).group_by(Purchase.status)).all()


def stock_balances(db):
    return db.execute(select(Material, InventoryBalance).outerjoin(InventoryBalance, Material.id == InventoryBalance.material_id)
        .order_by(Material.name, Material.id)).all()


def movement_counts(db, start, end):
    return db.execute(select(InventoryMovement.movement_type, func.count())
        .where(InventoryMovement.created_at >= start, InventoryMovement.created_at < end).group_by(InventoryMovement.movement_type)).all()


def completed_production_costs(db, start, end):
    return db.execute(select(Order, ProductionRecord).outerjoin(ProductionRecord, ProductionRecord.order_id == Order.id)
        .where(Order.status == "completed", Order.completed_at >= start, Order.completed_at < end)).all()


def production_records(db, start, end):
    return db.scalars(select(ProductionRecord).where(ProductionRecord.created_at >= start, ProductionRecord.created_at < end)).all()


def active_products(db, limit, offset):
    query = select(Product).where(Product.is_active.is_(True))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(Product.name, Product.id).limit(limit).offset(offset)).all()
    return rows, total


def recent_orders(db, date_from, date_to, limit):
    return db.scalars(select(Order).where(Order.order_date.between(date_from, date_to))
        .order_by(Order.created_at.desc(), Order.id).limit(limit)).all()


def recent_purchases(db, date_from, date_to, limit):
    return db.scalars(select(Purchase).where(Purchase.purchase_date.between(date_from, date_to))
        .order_by(Purchase.created_at.desc(), Purchase.id).limit(limit)).all()
