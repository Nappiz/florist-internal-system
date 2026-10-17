from uuid import uuid4
from decimal import Decimal,ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select
from models.supplier_material_model import SupplierMaterial
from crud import supplier_materials_crud as crud
from use_cases.common.persistence import finish
from use_cases.common.response import row_response,input_values
from use_cases.audit.record import record
from use_cases.supplier_materials.validate import validate

def create(db,actor,data):
    values=input_values(data)
    validate(db,values)
    row=crud.add(db,SupplierMaterial(id=uuid4(),**values))
    record(db,actor,'create','supplier_materials',row.id)
    finish(db)
    db.refresh(row)
    return respond(row)


def respond(row):
    result=row_response(row)
    result['normalized_unit_price']=str((Decimal(row.listed_price)/row.quantity_in_base_unit).quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP))
    return result
