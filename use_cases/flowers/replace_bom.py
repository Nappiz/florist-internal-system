from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from crud import flowers_crud
from models.flower_material_model import FlowerMaterial
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import normalize_materials
from use_cases.flowers.get_bom import get_bom


def replace_bom(db, actor, entity_id, data):
    entity = flowers_crud.get(db, UUID(str(entity_id)), lock=True)
    if entity is None:
        raise HTTPException(404, "Bunga tidak ditemukan.")
    if entity.is_active and not (data.materials):
        raise HTTPException(422, "Bunga aktif wajib memiliki komposisi.")
    materials = normalize_materials(db, data.materials)
    flowers_crud.clear_materials(db, entity.id)
    for line in materials:
        flowers_crud.add(db, FlowerMaterial(flower_id=entity.id, **line))
    entity.updated_at = datetime.now(UTC)
    record(db, actor, "replace_bom", "flower", entity.id)
    finish(db)
    return get_bom(db, entity.id)

