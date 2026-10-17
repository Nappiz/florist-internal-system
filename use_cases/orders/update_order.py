from datetime import UTC, datetime

from fastapi import HTTPException

from crud import orders_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.build_items import build_items
from use_cases.orders.calculate_totals import calculate_totals
from use_cases.orders.order_response import order_response
from use_cases.orders.validate_order import REQUIRED_FIELDS, payment_status, validate_order


def update_order(db, actor, order_id, data):
    values = data.model_dump(exclude_unset=True, exclude={"items", "price_override_reason"})
    if not data.model_fields_set or any(getattr(data, key) is None for key in REQUIRED_FIELDS & data.model_fields_set):
        raise HTTPException(422, "Isi perubahan valid; field wajib tidak boleh null.")
    if "items" in data.model_fields_set and data.items is None:
        raise HTTPException(422, "Item order tidak boleh null.")
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    if order.status != "draft":
        raise HTTPException(409, "Hanya order draft dapat diubah.")
    merged = {key: values.get(key, getattr(order, key)) for key in ("customer_name", "fulfillment_method", "customer_address", "order_date", "required_date", "sales_channel", "discount_amount", "shipping_charge")}
    validate_order(merged)
    rows = build_items(db, order.id, data.items, actor=actor, discount_amount=merged["discount_amount"], price_override_reason=data.price_override_reason) if "items" in data.model_fields_set else orders_crud.items(db, order.id)
    from use_cases.orders.build_items import validate_custom_order_price
    if "items" not in data.model_fields_set and merged["discount_amount"] != order.discount_amount:
        validate_custom_order_price(actor, rows, merged["discount_amount"], data.price_override_reason)
    values["subtotal"], values["total_amount"] = calculate_totals([{"quantity": row.quantity, "unit_price": row.unit_price} for row in rows], merged["discount_amount"], merged["shipping_charge"])
    paid = orders_crud.paid_amount(db, order.id)
    if values["total_amount"] < paid:
        raise HTTPException(409, "Total order tidak boleh lebih kecil dari pembayaran yang sudah diterima.")
    values.update(payment_status=payment_status(values["total_amount"], paid), updated_by=actor.user.id, updated_at=datetime.now(UTC))
    orders_crud.update(db, order, values)
    if "items" in data.model_fields_set:
        orders_crud.replace_items(db, order.id, rows)
    record(db, actor, "update", "order", order.id)
    if data.price_override_reason:
        record(db, actor, "price_override", "order", order.id, {"reason": data.price_override_reason})
    finish(db)
    return order_response(db, order)
