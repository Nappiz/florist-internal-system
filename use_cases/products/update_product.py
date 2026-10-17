from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from crud import products_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import mutation_values, validate_product_recipe
from use_cases.products.get_product import get_product


def update_product(db, actor, entity_id, data):
    entity = products_crud.get(db, UUID(str(entity_id)), lock=True)
    if entity is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    values = mutation_values(data)
    if values.get("is_active") is True:
        validate_product_recipe(db, entity.id)
    for key, value in values.items():
        setattr(entity, key, value)
    entity.updated_at = datetime.now(UTC)
    record(db, actor, "update", "product", entity.id, {"fields": sorted(values)})
    finish(db)
    return get_product(db, entity.id)

