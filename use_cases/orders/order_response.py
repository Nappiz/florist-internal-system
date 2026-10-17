from crud import orders_crud
from schemas.order_schema import OrderResponse
from use_cases.orders.validate_order import payment_status


def order_response(db, order):
    values = {key: getattr(order, key) for key in OrderResponse.model_fields if key not in {"paid_amount", "remaining_amount", "items", "payments", "production", "history"}}
    payments = orders_crud.payments(db, order.id)
    paid = sum(row.amount for row in payments if row.reversed_at is None)
    values.update(paid_amount=paid, remaining_amount=order.total_amount - paid, payment_status=payment_status(order.total_amount, paid), items=orders_crud.items(db, order.id), payments=payments, production=orders_crud.production(db, order.id))
    values['history']=orders_crud.history(db,order.id)
    return OrderResponse(**values)
