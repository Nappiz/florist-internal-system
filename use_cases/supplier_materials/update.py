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
from use_cases.supplier_materials.create import respond


def update(db,actor,identity,data):
    row=crud.get(db,identity)
    if row is None: raise HTTPException(404,'Data tidak ditemukan.')
    values=input_values(data,exclude_unset=True)
    if not values: raise HTTPException(422,'Isi minimal satu field.')
    validate(db,values,row)
    # Match purchasing lock order: store, material, then listing.
    row=crud.get(db,identity,lock=True)
    for key,value in values.items(): setattr(row,key,value)
    record(db,actor,'update','supplier_materials',row.id,{'fields':sorted(values)})
    finish(db)
    db.refresh(row)
    return respond(row)
