from uuid import UUID

from fastapi import HTTPException

from crud import flowers_crud
from use_cases.catalogue.costing import flower_recipe
from use_cases.catalogue.response import cost_response
from use_cases.catalogue.validation import validate_flower_recipe


def get_cost(db, entity_id):
    entity = flowers_crud.get(db, UUID(str(entity_id)))
    if entity is None:
        raise HTTPException(404, "Bunga tidak ditemukan.")
    return cost_response(db, entity, flower_recipe(db, entity.id), validate=lambda: validate_flower_recipe(db, entity.id, lock=False))

