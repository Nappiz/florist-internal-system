from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP, localcontext
from uuid import UUID

from fastapi import HTTPException

from crud import products_crud
from models.flower_model import Flower
from models.product_model import Product
from models.material_model import Material
from use_cases.catalogue.costing import flower_recipe, product_recipe
from use_cases.catalogue.validation import validate_flower_recipe, validate_product_recipe
from use_cases.common.validation import quantity, require_active


def snapshot_cost(value):
    if value is None:
        return None
    value = Decimal(value)
    if not value.is_finite() or value < 0 or value >= Decimal("1e30"):
        raise HTTPException(422, "Estimasi biaya melebihi batas pencatatan.")
    with localcontext() as context:
        context.prec = 60
        rounded = value.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    if rounded >= Decimal("1e30"):
        raise HTTPException(422, "Estimasi biaya melebihi batas pencatatan.")
    return rounded


def json_snapshot(value):
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, dict):
        return {key: json_snapshot(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_snapshot(item) for item in value]
    return value


def material_changes(items):
    quantities = defaultdict(Decimal)
    units = {}
    with localcontext() as context:
        context.prec = 60
        for item in items:
            if not item.recipe_snapshot or not item.recipe_snapshot.get("materials"):
                raise HTTPException(409, "Snapshot resep order belum tersedia.")
            for line in item.recipe_snapshot["materials"]:
                identity = UUID(line["material_id"])
                if identity in units and units[identity] != line["unit"]:
                    raise HTTPException(409, "Satuan snapshot material tidak konsisten.")
                units[identity] = line["unit"]
                quantities[identity] += Decimal(line["quantity"]) * item.quantity
        return [{"material_id": identity, "quantity_delta": -quantity(amount)} for identity, amount in sorted(quantities.items(), key=lambda item: str(item[0]))]


def snapshot_order(db, items):
    from use_cases.custom_bouquets.validated_configuration import validated_configuration
    from use_cases.orders.lock_references import lock_references
    lock_references(db,items)
    custom_items=[item for item in items if item.custom_bouquet_id]
    for item in sorted(custom_items,key=lambda item:str(item.custom_bouquet_id)):
        config=validated_configuration(db,item.custom_bouquet_id)
        # Draft order captured the finalized recipe and negotiated price. Never reprice here.
        recipe=item.recipe_snapshot or {**config.recipe_snapshot,"personalization":dict(config.personalization),"configuration_id":str(config.id)}
        item.recipe_snapshot=json_snapshot(recipe)
        item.labor_cost_snapshot=snapshot_cost(recipe["labor_cost"])
        item.estimated_hpp_snapshot=snapshot_cost(recipe["estimated_hpp"])
        item.cost_complete=recipe["cost_complete"]
    standard_items=[item for item in items if not item.custom_bouquet_id]
    product_ids = sorted({item.product_id for item in standard_items if item.product_id}, key=str)
    products = {identity: require_active(db, Product, identity) for identity in product_ids}
    flower_ids = {item.flower_id for item in standard_items if item.flower_id}
    for identity in product_ids:
        flower_ids.update(row.flower_id for row in products_crud.flowers(db, identity))
    flowers = {identity: require_active(db, Flower, identity) for identity in sorted(flower_ids, key=str)}
    recipes = {}
    for item in standard_items:
        key = (item.product_id is not None, item.product_id or item.flower_id)
        if key not in recipes:
            recipes[key] = product_recipe(db, key[1]) if key[0] else flower_recipe(db, key[1])
    material_ids = {UUID(line["material_id"]) for recipe in recipes.values() for line in recipe["materials"]}
    for identity in sorted(material_ids, key=str):
        require_active(db, Material, identity)
    for identity in product_ids:
        validate_product_recipe(db, identity)
    for identity in sorted(flower_ids, key=str):
        validate_flower_recipe(db, identity)
    for item in standard_items:
        key = (item.product_id is not None, item.product_id or item.flower_id)
        catalogue = products[key[1]] if key[0] else flowers[key[1]]
        recipe = recipes[key]
        item.item_name_snapshot = catalogue.name
        item.recipe_snapshot = json_snapshot(recipe)
        item.labor_cost_snapshot = snapshot_cost(recipe["labor_cost"])
        item.estimated_hpp_snapshot = snapshot_cost(recipe["estimated_hpp"])
        item.cost_complete = recipe["cost_complete"]
    # Validate the final aggregate once; recipes can contain fractional components.
    material_changes(items)
