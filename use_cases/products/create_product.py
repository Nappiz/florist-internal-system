from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from crud import products_crud
from models.product_model import Product
from models.product_material_model import ProductMaterial
from models.product_flower_model import ProductFlower
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.catalogue.validation import mutation_values, normalize_materials, normalize_flowers
from use_cases.products.get_product import get_product


def create_product(db, actor, data):
    bom = data.bom
    if data.is_active and (bom is None or not (bom.flowers or bom.materials)):
        raise HTTPException(422, "Produk aktif wajib memiliki komposisi.")
    flowers = normalize_flowers(db, bom.flowers, bom.materials) if bom else []
    materials = normalize_materials(db, bom.materials) if bom else []
    values = mutation_values(data, exclude={"bom"})
    entity = Product(id=uuid4(), **values)
    products_crud.add(db, entity)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU produk sudah digunakan atau data tidak valid.") from None
    for line in materials:
        products_crud.add(db, ProductMaterial(product_id=entity.id, **line))
    for line in flowers:
        products_crud.add(db, ProductFlower(product_id=entity.id, **line))
    record(db, actor, "create", "product", entity.id)
    finish(db)
    return get_product(db, entity.id)

