from uuid import uuid4
from decimal import Decimal,ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select
from models.supplier_store_model import SupplierStore
from crud import supplier_stores_crud as crud
from use_cases.common.persistence import finish
from use_cases.common.response import row_response,input_values
from use_cases.audit.record import record
from use_cases.supplier_stores.validate import validate

def create(db,actor,data):
    values=input_values(data)
    validate(db,values)
    row=crud.add(db,SupplierStore(id=uuid4(),**values))
    record(db,actor,'create','supplier_stores',row.id)
    finish(db)
    db.refresh(row)
    return respond(row)


def respond(row):
    result=row_response(row)
    return result
