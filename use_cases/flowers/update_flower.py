from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from crud import flowers_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import mutation_values, validate_flower_recipe
from use_cases.flowers.get_flower import get_flower


def update_flower(db, actor, entity_id, data):
    entity = flowers_crud.get(db, UUID(str(entity_id)), lock=True)
    if entity is None:
        raise HTTPException(404, "Bunga tidak ditemukan.")
    values = mutation_values(data)
    if values.get("is_active") is True:
        validate_flower_recipe(db, entity.id)
    for key, value in values.items():
        setattr(entity, key, value)
    entity.updated_at = datetime.now(UTC)
    record(db, actor, "update", "flower", entity.id, {"fields": sorted(values)})
    finish(db)
    return get_flower(db, entity.id)

