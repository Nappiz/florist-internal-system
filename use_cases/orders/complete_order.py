from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response


def complete_order(db, actor, order_id):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status != "ready":
        raise HTTPException(409, "Hanya order ready dapat diselesaikan.")
    order.status = "completed"
    order.completed_at = order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "complete", "order", order.id)
    finish(db)
    return order_response(db, order)
