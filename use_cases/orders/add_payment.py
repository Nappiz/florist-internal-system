from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from models.order_payment_model import OrderPayment
from use_cases.cashflow.post_payment import post_payment
from use_cases.cashflow.common import require_accounts
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.order_response import order_response
from use_cases.orders.validate_order import payment_status, today


def add_payment(db, actor, order_id, data):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status == "cancelled":
        raise HTTPException(409, "Pembayaran tidak dapat ditambahkan ke order cancelled.")
    values = data.model_dump()
    if "payment_date" not in data.model_fields_set:
        values["payment_date"] = today()
    if values["payment_date"] is None or values["payment_date"] > today():
        raise HTTPException(422, "Tanggal pembayaran wajib dan tidak boleh di masa depan.")
    existing = orders_crud.payment_by_key(db, order.id, data.payment_key)
    if existing is not None:
        # Omitting date on a retry preserves the original default across midnight.
        compared = data.model_dump(exclude_unset=True)
        if any(getattr(existing, key) != value for key, value in compared.items()):
            raise HTTPException(409, "Kunci pembayaran sudah digunakan dengan data berbeda.")
        return order_response(db, order)
    paid = orders_crud.paid_amount(db, order.id)
    if paid + data.amount > order.total_amount:
        raise HTTPException(409, "Pembayaran melebihi sisa tagihan order.")
    require_accounts(db, [data.cash_account_id], values["payment_date"])
    payment = orders_crud.add(db, OrderPayment(order_id=order.id, **values, created_by=actor.user.id))
    post_payment(db, actor, "order_payment", payment)
    order.payment_status = payment_status(order.total_amount, paid + data.amount)
    order.updated_at = datetime.now(UTC)
    order.updated_by = actor.user.id
    record(db, actor, "payment", "order", order.id, {"payment_key": str(data.payment_key), "amount": data.amount})
    finish(db)
    return order_response(db, order)
