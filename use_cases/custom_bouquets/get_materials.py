from decimal import Decimal
from uuid import UUID
from models.inventory_balance_model import InventoryBalance
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.orders.snapshot_order import json_snapshot

def get_materials(db,identity):
    row=get_bouquet(db,identity)
    materials=[]
    for line in row.recipe_snapshot.get("materials",[]):
        balance=db.get(InventoryBalance,UUID(line["material_id"]))
        stock=Decimal(balance.quantity_on_hand) if balance else Decimal(0)
        materials.append({**line,"current_stock":stock,"shortage_quantity":max(Decimal(0),Decimal(line["quantity"])-stock)})
    availability="unknown" if not row.cost_complete or not materials else ("insufficient_stock" if any(line["shortage_quantity"]>0 for line in materials) else "available")
    return json_snapshot({"materials":materials,"availability":availability,"cost_complete":row.cost_complete,"incomplete_reasons":row.recipe_snapshot.get("incomplete_reasons",[])})
