from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response
from use_cases.orders.snapshot_order import snapshot_order


def confirm_order(db, actor, order_id):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status != "draft":
        raise HTTPException(409, "Hanya order draft dapat dikonfirmasi.")
    items = orders_crud.items(db, order.id)
    if not items:
        raise HTTPException(409, "Order wajib memiliki minimal satu item.")
    snapshot_order(db, items)
    order.status = "confirmed"
    order.confirmed_at = order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "confirm", "order", order.id)
    finish(db)
    return order_response(db, order)
