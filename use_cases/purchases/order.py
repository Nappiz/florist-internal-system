from fastapi import HTTPException
from models.supplier_store_model import SupplierStore
from models.material_model import Material
from models.supplier_material_model import SupplierMaterial
from crud import purchases_crud
from use_cases.common.validation import require_active
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.purchases.response import require,response


def order(db,actor,identity):
    purchase=require(db,identity)
    if purchase.status!='draft': raise HTTPException(409,'Hanya draft dapat dipesan.')
    require_active(db,SupplierStore,purchase.supplier_id)
    for item in sorted(purchases_crud.items(db,identity),key=lambda row:str(row.material_id)):
        require_active(db,Material,item.material_id)
        if item.supplier_listing_id: require_active(db,SupplierMaterial,item.supplier_listing_id)
    purchase.status='ordered'
    purchase.updated_by=actor.user.id
    record(db,actor,'order','purchase',identity)
    finish(db)
    return response(db,purchase)
