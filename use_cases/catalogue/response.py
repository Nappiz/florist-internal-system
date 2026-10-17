from decimal import Decimal, ROUND_HALF_UP

from use_cases.catalogue.availability import available_quantity
from use_cases.catalogue.precision import cost_precision


@cost_precision()
def cost_response(db, entity, recipe, *, validate=None):
    hpp = recipe["estimated_hpp"]
    profit = Decimal(entity.selling_price) - hpp if hpp is not None else None
    return {
        **recipe,
        "estimated_material_cost": hpp - recipe["labor_cost"] if hpp is not None else None,
        "estimated_profit": profit,
        "estimated_margin": (profit / Decimal(entity.selling_price) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if profit is not None and entity.selling_price else None,
        "available_quantity": available_quantity(db, recipe, validate=validate) if entity.is_active else 0,
    }


def entity_response(db, entity, recipe, *, validate=None):
    fields = ("id", "sku", "name", "category", "description", "image_url", "selling_price", "is_active", "created_at", "updated_at")
    result = {key: getattr(entity, key) for key in fields}
    for key in ("estimated_labor_cost", "assembly_labor_cost"):
        if hasattr(entity, key):
            result[key] = getattr(entity, key)
    return {**result, **cost_response(db, entity, recipe, validate=validate)}

