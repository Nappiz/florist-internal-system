from crud import reports_crud
from use_cases.reports.period import resolve_period


def sales_report(db, actor, query):
    period, start, end = resolve_period(query)
    orders = reports_crud.completed_orders(db, start, end)
    payments = reports_crud.payments(db, period["date_from"], period["date_to"])
    channels = {}
    for order in orders:
        row = channels.setdefault(order.sales_channel, {"sales_channel": order.sales_channel, "order_count": 0, "total_amount": 0})
        row["order_count"] += 1
        row["total_amount"] += order.total_amount
    items = {}
    for item in reports_crud.completed_items(db, start, end):
        key = str(item.product_id or item.flower_id)
        row = items.setdefault(key, {"item_id": key, "item_type": "product" if item.product_id else "flower",
            "item_name": item.item_name_snapshot, "quantity": 0, "subtotal": 0})
        row["quantity"] += item.quantity
        row["subtotal"] += item.subtotal
    statuses = dict(reports_crud.order_status_counts(db, period["date_from"], period["date_to"]))
    return {"period": period, "completed_order_count": len(orders), "completed_sales_total": sum(row.total_amount for row in orders),
        "collections_total": sum(payment.amount for payment, _ in payments),
        "collections_from_cancelled_orders": sum(payment.amount for payment, status in payments if status == "cancelled"),
        "order_count": sum(statuses.values()), "orders_by_status": statuses,
        "by_sales_channel": sorted(channels.values(), key=lambda row: (-row["total_amount"], row["sales_channel"]))[:query.limit],
        "top_items": sorted(items.values(), key=lambda row: (-row["quantity"], row["item_id"]))[:query.limit], "top_limit": query.limit}
