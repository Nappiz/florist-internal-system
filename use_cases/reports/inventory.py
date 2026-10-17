from datetime import UTC, datetime
from decimal import Decimal, localcontext

from crud import reports_crud
from use_cases.reports.period import resolve_period


def inventory_report(db, actor, query):
    period, start, end = resolve_period(query)
    items = []
    low_stock = []
    missing_cost = 0
    value = Decimal(0)
    with localcontext() as context:
        context.prec = 64
        for material, balance in reports_crud.stock_balances(db):
            quantity = balance.quantity_on_hand if balance else Decimal(0)
            known_cost = balance is not None and balance.has_received_cost
            unit_cost = balance.average_unit_cost if known_cost else None
            item_value = quantity * unit_cost if known_cost else Decimal(0) if quantity == 0 else None
            if item_value is None:
                missing_cost += 1
            else:
                value += item_value
            row = {"material_id": str(material.id), "sku": material.sku, "name": material.name, "base_unit": material.base_unit,
                "is_active": material.is_active, "quantity_on_hand": quantity, "minimum_stock": material.minimum_stock,
                "average_unit_cost": unit_cost, "inventory_value": item_value}
            items.append(row)
            if material.is_active and quantity <= material.minimum_stock:
                low_stock.append(row)
    return {"period": period, "as_of": datetime.now(UTC), "inventory_value": value if missing_cost == 0 else None,
        "known_inventory_value": value, "valuation_complete": missing_cost == 0, "missing_cost_material_count": missing_cost,
        "low_stock_count": len(low_stock), "low_stock": low_stock[:query.limit],
        "movements_by_type": dict(reports_crud.movement_counts(db, start, end)),
        "items": items[query.offset:query.offset + query.limit], "total": len(items), "limit": query.limit, "offset": query.offset}
