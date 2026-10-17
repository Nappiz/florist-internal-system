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


def list_rows(db,actor,query):
    rows,total=crud.list_rows(db,query)
    return {'items':[respond(row) for row in rows],'total':total,'limit':query.limit,'offset':query.offset}
