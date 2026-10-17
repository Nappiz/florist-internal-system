from fastapi import HTTPException
from crud import orders_crud
from use_cases.orders.order_response import order_response


def get_order(db, order_id):
    order = orders_crud.get(db, order_id)
    if order is None:
        raise HTTPException(404, "Order tidak ditemukan.")
    return order_response(db, order)
