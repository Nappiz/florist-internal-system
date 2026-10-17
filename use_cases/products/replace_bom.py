from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from crud import products_crud
from models.product_material_model import ProductMaterial
from models.product_flower_model import ProductFlower
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import normalize_materials, normalize_flowers
from use_cases.products.get_bom import get_bom


def replace_bom(db, actor, entity_id, data):
    entity = products_crud.get(db, UUID(str(entity_id)), lock=True)
    if entity is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    if entity.is_active and not (data.flowers or data.materials):
        raise HTTPException(422, "Produk aktif wajib memiliki komposisi.")
    flowers = normalize_flowers(db, data.flowers, data.materials)
    materials = normalize_materials(db, data.materials)
    products_crud.clear_materials(db, entity.id)
    products_crud.clear_flowers(db, entity.id)
    for line in materials:
        products_crud.add(db, ProductMaterial(product_id=entity.id, **line))
    for line in flowers:
        products_crud.add(db, ProductFlower(product_id=entity.id, **line))
    entity.updated_at = datetime.now(UTC)
    record(db, actor, "replace_bom", "product", entity.id)
    finish(db)
    return get_bom(db, entity.id)

