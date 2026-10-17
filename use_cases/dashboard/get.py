from crud import reports_crud
from use_cases.reports.inventory import inventory_report
from use_cases.reports.purchases import purchases_report
from use_cases.reports.sales import sales_report


def dashboard(db, actor, query):
    sales = sales_report(db, actor, query)
    purchases = purchases_report(db, actor, query)
    inventory = inventory_report(db, actor, query)
    period = sales["period"]
    orders = reports_crud.recent_orders(db, period["date_from"], period["date_to"], query.limit)
    recent_purchases = reports_crud.recent_purchases(db, period["date_from"], period["date_to"], query.limit)
    statuses=sales['orders_by_status']
    return {"period": period, "completed_sales_total": sales["completed_sales_total"], "collections_total": sales["collections_total"],
        'active_orders':sum(statuses.get(status,0) for status in ('draft','confirmed','in_production','ready')),
        'awaiting_production':statuses.get('confirmed',0), 'ready_for_fulfillment':statuses.get('ready',0), 'completed_orders':sales['completed_order_count'],
        "received_purchases_total": purchases["total_amount"], "inventory_value": inventory["inventory_value"],
        "low_stock_count": inventory["low_stock_count"], "low_stock": inventory["low_stock"], "order_status_counts": sales["orders_by_status"],
        "purchase_status_counts": dict(reports_crud.purchase_status_counts(db, period["date_from"], period["date_to"])),
        "recent_orders": [{"id": str(row.id), "order_number": row.order_number, "customer_name": row.customer_name,
            "status": row.status, "payment_status": row.payment_status, "total_amount": row.total_amount} for row in orders],
        "recent_purchases": [{"id": str(row.id), "purchase_number": row.purchase_number, "supplier_id": str(row.supplier_id),
            "status": row.status, "payment_status": row.payment_status, "total_amount": row.total_amount} for row in recent_purchases], "limit": query.limit}
