from uuid import uuid4
from decimal import Decimal,ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select
from models.material_model import Material
from crud import materials_crud as crud
from use_cases.common.persistence import finish
from use_cases.common.response import row_response,input_values
from use_cases.audit.record import record
from use_cases.materials.validate import validate
from use_cases.materials.create import respond


def get(db,actor,identity):
    row=crud.get(db,identity)
    if row is None: raise HTTPException(404,'Data tidak ditemukan.')
    return respond(row)
