from uuid import uuid4
from decimal import Decimal,ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select
from models.material_model import Material
from crud import materials_crud as crud
from use_cases.common.persistence import finish,flush
from use_cases.common.response import row_response,input_values
from use_cases.audit.record import record
from use_cases.materials.validate import validate

def create(db,actor,data):
    values=input_values(data)
    validate(db,values)
    row=crud.add(db,Material(id=uuid4(),**values))
    flush(db)
    from models.inventory_balance_model import InventoryBalance
    db.add(InventoryBalance(material_id=row.id))
    record(db,actor,'create','materials',row.id)
    finish(db)
    db.refresh(row)
    return respond(row)


def respond(row):
    result=row_response(row)
    return result
