from decimal import Decimal, localcontext

from crud import reports_crud
from use_cases.reports.period import resolve_period


def purchases_report(db, actor, query):
    period, _, _ = resolve_period(query)
    purchases = reports_crud.received_purchases(db, period["date_from"], period["date_to"])
    suppliers = {}
    for purchase, name in purchases:
        row = suppliers.setdefault(str(purchase.supplier_id), {"supplier_id": str(purchase.supplier_id), "supplier_name": name, "purchase_count": 0, "total_amount": 0})
        row["purchase_count"] += 1
        row["total_amount"] += purchase.total_amount
    materials = {}
    with localcontext() as context:
        context.prec = 64
        for item in reports_crud.received_purchase_items(db, period["date_from"], period["date_to"]):
            row = materials.setdefault(str(item.material_id), {"material_id": str(item.material_id), "material_name": item.material_name_snapshot,
                "base_unit": item.base_unit_snapshot, "quantity": Decimal(0), "subtotal": 0})
            row["quantity"] += item.quantity_base
            row["subtotal"] += item.subtotal
    return {"period": period, "purchase_count": len(purchases), "total_amount": sum(row.total_amount for row, _ in purchases),
        "by_supplier": sorted(suppliers.values(), key=lambda row: (-row["total_amount"], row["supplier_id"]))[:query.limit],
        "top_materials": sorted(materials.values(), key=lambda row: (-row["subtotal"], row["material_id"]))[:query.limit], "top_limit": query.limit}
