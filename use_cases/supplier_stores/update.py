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
from use_cases.supplier_stores.create import respond


def update(db,actor,identity,data):
    row=crud.get(db,identity,lock=True)
    if row is None: raise HTTPException(404,'Data tidak ditemukan.')
    values=input_values(data,exclude_unset=True)
    if not values: raise HTTPException(422,'Isi minimal satu field.')
    validate(db,values,row)
    for key,value in values.items(): setattr(row,key,value)
    record(db,actor,'update','supplier_stores',row.id,{'fields':sorted(values)})
    finish(db)
    db.refresh(row)
    return respond(row)
