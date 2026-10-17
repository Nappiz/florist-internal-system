from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from crud import flowers_crud
from models.flower_model import Flower
from models.flower_material_model import FlowerMaterial
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import mutation_values, normalize_materials
from use_cases.flowers.get_flower import get_flower


def create_flower(db, actor, data):
    bom = data.bom
    if data.is_active and (bom is None or not (bom.materials)):
        raise HTTPException(422, "Bunga aktif wajib memiliki komposisi.")
    materials = normalize_materials(db, bom.materials) if bom else []
    values = mutation_values(data, exclude={"bom"})
    entity = Flower(id=uuid4(), **values)
    flowers_crud.add(db, entity)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU bunga sudah digunakan atau data tidak valid.") from None
    for line in materials:
        flowers_crud.add(db, FlowerMaterial(flower_id=entity.id, **line))
    record(db, actor, "create", "flower", entity.id)
    finish(db)
    return get_flower(db, entity.id)

