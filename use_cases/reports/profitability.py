from decimal import Decimal, localcontext

from crud import reports_crud
from use_cases.catalogue.costing import product_recipe
from use_cases.reports.period import resolve_period


def profitability_report(db, actor, query):
    period, start, end = resolve_period(query)
    rows = reports_crud.completed_production_costs(db, start, end)
    revenue = sum(order.subtotal - order.discount_amount for order, _ in rows)
    missing_cost = sum(record is None for _, record in rows)
    with localcontext() as context:
        context.prec = 64
        completed_cost = sum((record.total_production_cost for _, record in rows if record is not None), Decimal(0))
        actual_cost = sum((record.total_production_cost for record in reports_crud.production_records(db, start, end)), Decimal(0))
        margin = Decimal(revenue) - completed_cost if missing_cost == 0 else None
        percent = margin / Decimal(revenue) * 100 if margin is not None and revenue > 0 else None
    products, total = reports_crud.active_products(db, query.limit, query.offset)
    estimates = []
    for product in products:
        recipe = product_recipe(db, product.id)
        estimates.append({"product_id": str(product.id), "sku": product.sku, "name": product.name,
            "selling_price": product.selling_price, "estimated_hpp": recipe["estimated_hpp"], "cost_complete": recipe["cost_complete"],
            "cost_sources": recipe["cost_sources"]})
    return {"period": period, "completed_revenue_excluding_shipping": revenue, "completed_production_cost": completed_cost,
        "completed_order_count": len(rows), "missing_production_cost_count": missing_cost, "cost_complete": missing_cost == 0,
        "gross_margin": margin, "gross_margin_percent": percent, "actual_production_cost": actual_cost,
        "estimated_product_hpp": estimates, "products_total": total, "limit": query.limit, "offset": query.offset}
