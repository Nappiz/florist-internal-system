from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response


def cancel_order(db, actor, order_id, data):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status not in {"draft", "confirmed", "in_production"}:
        raise HTTPException(409, "Order ready/completed/cancelled tidak dapat dibatalkan pada alur MVP.")
    order.status = "cancelled"
    order.cancellation_reason = data.reason
    order.cancelled_at = order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "cancel", "order", order.id, {"reason": data.reason})
    finish(db)
    return order_response(db, order)
