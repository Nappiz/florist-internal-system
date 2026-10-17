from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from crud import flowers_crud, products_crud
from models.inventory_balance_model import InventoryBalance
from models.supplier_material_model import SupplierMaterial
from models.supplier_store_model import SupplierStore
from use_cases.catalogue.precision import cost_precision


@cost_precision()
def material_cost(db, material_id):
    material_id = UUID(str(material_id))
    balance = db.get(InventoryBalance, material_id)
    if balance is not None and balance.has_received_cost:
        return {"unit_cost": Decimal(balance.average_unit_cost), "source": "inventory"}
    listings = db.scalars(
        select(SupplierMaterial)
        .join(SupplierStore, SupplierStore.id == SupplierMaterial.supplier_id)
        .where(SupplierMaterial.material_id == material_id, SupplierMaterial.is_active.is_(True), SupplierStore.is_active.is_(True))
    ).all()
    prices = [Decimal(row.listed_price) / Decimal(row.quantity_in_base_unit) for row in listings if row.quantity_in_base_unit > 0]
    if prices:
        return {"unit_cost": min(prices).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP), "source": "listing"}
    return {"unit_cost": None, "source": "missing"}


@cost_precision()
def _estimate(db, materials, labor_cost):
    sources = []
    total = Decimal(labor_cost)
    complete = bool(materials)
    for line in materials:
        cost = material_cost(db, line["material_id"])
        sources.append({"material_id": line["material_id"], **cost})
        if cost["unit_cost"] is None:
            complete = False
        else:
            total += line["quantity"] * cost["unit_cost"]
    return {
        "materials": materials,
        "labor_cost": Decimal(labor_cost),
        "estimated_hpp": total if complete else None,
        "cost_complete": complete,
        "cost_sources": sources,
    }


def flower_recipe(db, flower_id):
    flower = flowers_crud.get(db, UUID(str(flower_id)))
    if flower is None:
        raise HTTPException(404, "Bunga tidak ditemukan.")
    materials = [{"material_id": str(row.material_id), "quantity": Decimal(row.quantity_required), "unit": row.unit} for row in flowers_crud.materials(db, flower.id)]
    return _estimate(db, materials, Decimal(flower.estimated_labor_cost))


@cost_precision()
def product_recipe(db, product_id):
    product = products_crud.get(db, UUID(str(product_id)))
    if product is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    quantities = {}
    labor = Decimal(product.assembly_labor_cost)
    component_complete = True
    for row in products_crud.flowers(db, product.id):
        recipe = flower_recipe(db, row.flower_id)
        labor += recipe["labor_cost"] * row.quantity_required
        component_complete = component_complete and bool(recipe["materials"])
        for material in recipe["materials"]:
            key = (material["material_id"], material["unit"])
            quantities[key] = quantities.get(key, Decimal(0)) + material["quantity"] * row.quantity_required
    # These quantities describe extra material used directly by the product.
    # Flower material is already expanded above, so each explicit extra is added once.
    for row in products_crud.materials(db, product.id):
        key = (str(row.material_id), row.unit)
        quantities[key] = quantities.get(key, Decimal(0)) + row.quantity_required
    materials = [{"material_id": material_id, "quantity": quantity, "unit": unit} for (material_id, unit), quantity in sorted(quantities.items())]
    result = _estimate(db, materials, labor)
    if not component_complete:
        result["cost_complete"] = False
        result["estimated_hpp"] = None
    return result

