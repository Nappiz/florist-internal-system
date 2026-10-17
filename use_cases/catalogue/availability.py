from decimal import Decimal, ROUND_FLOOR
from uuid import UUID

from fastapi import HTTPException

from models.inventory_balance_model import InventoryBalance
from models.material_model import Material


def available_quantity(db, recipe, *, validate=None):
    if not recipe["materials"]:
        return 0
    if validate is not None:
        try:
            validate()
        except HTTPException:
            return 0
    amounts = []
    for line in recipe["materials"]:
        material_id = UUID(str(line["material_id"]))
        material = db.get(Material, material_id)
        balance = db.get(InventoryBalance, material_id)
        if material is None or not material.is_active or balance is None:
            return 0
        count = (Decimal(balance.quantity_on_hand) / line["quantity"]).to_integral_value(rounding=ROUND_FLOOR)
        amounts.append(max(0, int(count)))
    return min(amounts)

