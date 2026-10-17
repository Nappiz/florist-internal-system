from sqlalchemy import select
from models.inventory_balance_model import InventoryBalance
from models.inventory_movement_model import InventoryMovement


def lock_balances(db,ids):
    return list(db.scalars(select(InventoryBalance).where(InventoryBalance.material_id.in_(ids)).order_by(InventoryBalance.material_id).with_for_update().execution_options(populate_existing=True)))


def get_balance(db,identity):
    return db.get(InventoryBalance,identity)


def get_event(db,event_key):
    return db.scalar(select(InventoryMovement).where(InventoryMovement.event_key==event_key))
