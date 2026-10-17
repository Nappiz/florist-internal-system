from decimal import Decimal
from fastapi import HTTPException
from crud import purchases_crud
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.inventory.move_stock import move_stock
from use_cases.purchases.response import require,response


def receive(db,actor,identity):
    purchase=require(db,identity)
    if purchase.status!='ordered': raise HTTPException(409,'Hanya pembelian ordered dapat diterima satu kali.')
    changes=[{'material_id':item.material_id,'quantity_delta':item.quantity_base,'unit_cost':Decimal(item.subtotal)/item.quantity_base} for item in purchases_crud.items(db,identity)]
    move_stock(db,actor,changes,'purchase_received',identity)
    purchase.status='received'
    purchase.updated_by=actor.user.id
    record(db,actor,'receive','purchase',identity)
    finish(db)
    return response(db,purchase)
