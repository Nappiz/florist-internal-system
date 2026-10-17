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

def archive(db,actor,identity):
    row=crud.get(db,identity,lock=True)
    if row is None: raise HTTPException(404,'Data tidak ditemukan.')
    row.is_active=False
    record(db,actor,'archive','supplier_materials',row.id)
    finish(db)
