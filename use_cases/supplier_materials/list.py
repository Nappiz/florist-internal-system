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


def list_rows(db,actor,query):
    if query.min_price is not None and query.max_price is not None and query.min_price>query.max_price: raise HTTPException(422,'Rentang harga tidak valid.')
    rows,total=crud.list_rows(db,query)
    return {'items':[respond(row) for row in rows],'total':total,'limit':query.limit,'offset':query.offset}
