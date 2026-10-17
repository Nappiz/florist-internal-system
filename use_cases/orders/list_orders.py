from fastapi import HTTPException
from crud import orders_crud
from models.order_model import Order
from schemas.order_schema import OrderPage
from use_cases.orders.order_response import order_response


def list_orders(db, filters):
    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise HTTPException(422, "Rentang tanggal tidak valid.")
    order_by = {"newest": Order.created_at.desc(), "oldest": Order.created_at.asc(), "required_date": Order.required_date.asc().nulls_last(), "total_asc": Order.total_amount.asc(), "total_desc": Order.total_amount.desc()}[filters.sort]
    return OrderPage(items=[order_response(db, row) for row in orders_crud.list_orders(db, filters, order_by)], total=orders_crud.count(db, filters), limit=filters.limit, offset=filters.offset)
