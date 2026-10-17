from uuid import UUID

from fastapi import HTTPException

from crud import products_crud
from use_cases.catalogue.costing import product_recipe
from use_cases.catalogue.response import entity_response
from use_cases.catalogue.validation import validate_product_recipe


def get_product(db, entity_id):
    entity = products_crud.get(db, UUID(str(entity_id)))
    if entity is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    return entity_response(db, entity, product_recipe(db, entity.id), validate=lambda: validate_product_recipe(db, entity.id, lock=False))

