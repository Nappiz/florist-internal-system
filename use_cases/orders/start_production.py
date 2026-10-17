from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response


def start_production(db, actor, order_id):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status != "confirmed":
        raise HTTPException(409, "Produksi hanya dapat dimulai dari order confirmed.")
    order.status = "in_production"
    order.production_started_at = order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "start_production", "order", order.id)
    finish(db)
    return order_response(db, order)
