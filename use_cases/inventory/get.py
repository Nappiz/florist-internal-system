from fastapi import HTTPException
from decimal import localcontext
from models.material_model import Material
from crud import inventory_crud
from use_cases.common.response import row_response


def get(db,actor,identity):
    row=inventory_crud.get_balance(db,identity)
    if row is None: raise HTTPException(404,'Material tidak ditemukan.')
    material=db.get(Material,identity)
    result=row_response(row)
    with localcontext() as context:
        context.prec=60
        inventory_value=str(row.quantity_on_hand*row.average_unit_cost)
    result.update(material_name=material.name,sku=material.sku,base_unit=material.base_unit,minimum_stock=str(material.minimum_stock),is_active=material.is_active,is_low_stock=row.quantity_on_hand<=material.minimum_stock,inventory_value=inventory_value)
    return result
