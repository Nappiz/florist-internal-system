from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP, localcontext

from fastapi import HTTPException

from crud import orders_crud
from models.production_record_model import ProductionRecord
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response
from use_cases.orders.snapshot_order import material_changes


def complete_production(db, actor, order_id):
    from use_cases.inventory.move_stock import move_stock

    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status != "in_production" or orders_crud.production(db, order.id) is not None:
        raise HTTPException(409, "Produksi hanya dapat diselesaikan sekali dari status in_production.")
    items = orders_crud.items(db, order.id)
    changes = material_changes(items)
    # Inventory updates, movement events, production record, and status share this transaction.
    with localcontext() as context:
        context.prec = 60
        material_cost = Decimal(move_stock(db, actor, changes, "production", order.id)).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        labor = sum((item.labor_cost_snapshot * item.quantity for item in items), Decimal("0")).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        total = material_cost + labor
        if any(not value.is_finite() or value < 0 or value >= Decimal("1e30") for value in (material_cost, labor, total)):
            raise HTTPException(422, "Biaya produksi melebihi batas pencatatan.")
        orders_crud.add(db, ProductionRecord(order_id=order.id, actual_material_cost=material_cost, labor_cost_snapshot=labor, total_production_cost=total, created_by=actor.user.id))
    order.status = "ready"
    order.ready_at = order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "complete_production", "order", order.id)
    finish(db)
    return order_response(db, order)
