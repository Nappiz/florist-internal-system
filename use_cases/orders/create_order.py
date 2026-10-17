from datetime import UTC, datetime
from uuid import uuid4

from crud import orders_crud
from models.order_model import Order
from schemas.order_schema import OrderResponse
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.build_items import build_items
from use_cases.orders.calculate_totals import calculate_totals
from use_cases.orders.order_response import order_response
from use_cases.orders.validate_order import payment_status, today, validate_order


def create_order(db, actor, data) -> OrderResponse:
    values = data.model_dump(exclude={"items", "price_override_reason"})
    if "order_date" not in data.model_fields_set:
        values["order_date"] = today()
    validate_order(values)
    identity = uuid4()
    items = build_items(db, identity, data.items, actor=actor, discount_amount=data.discount_amount, price_override_reason=data.price_override_reason)
    values["subtotal"], values["total_amount"] = calculate_totals([{"quantity": item.quantity, "unit_price": item.unit_price} for item in items], values["discount_amount"], values["shipping_charge"])
    values["payment_status"] = payment_status(values["total_amount"], 0)
    now = datetime.now(UTC)
    order = orders_crud.add(db, Order(id=identity, order_number="ORD-" + identity.hex.upper(), **values, created_by=actor.user.id, updated_by=actor.user.id, created_at=now, updated_at=now))
    orders_crud.replace_items(db, order.id, items)
    record(db, actor, "create", "order", order.id)
    if data.price_override_reason:
        record(db, actor, "price_override", "order", order.id, {"reason": data.price_override_reason})
    finish(db)
    return order_response(db, order)
