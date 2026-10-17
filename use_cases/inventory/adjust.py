from fastapi import HTTPException
from models.material_model import Material
from crud import inventory_crud
from use_cases.common.validation import require_active
from use_cases.common.persistence import finish
from use_cases.common.response import row_response
from use_cases.audit.record import record
from use_cases.inventory.move_stock import move_stock


def adjust(db,actor,data):
    if not actor.user.is_superadmin: raise HTTPException(403,'Hanya superadmin dapat menyesuaikan stok.')
    if data.quantity_delta==0: raise HTTPException(422,'Perubahan stok tidak boleh nol.')
    if data.quantity_delta>0 and data.unit_cost is None: raise HTTPException(422,'Biaya unit diperlukan untuk stok masuk.')
    require_active(db,Material,data.material_id)
    event=f'adjustment:{data.adjustment_key}:{data.material_id}'
    if inventory_crud.get_event(db,event): raise HTTPException(409,'Penyesuaian sudah diproses.')
    move_stock(db,actor,[{'material_id':data.material_id,'quantity_delta':data.quantity_delta,'unit_cost':data.unit_cost or 0,'notes':data.reason}],'adjustment',data.adjustment_key)
    record(db,actor,'adjustment','inventory',data.material_id,{'adjustment_key':str(data.adjustment_key),'quantity_delta':str(data.quantity_delta),'reason':data.reason})
    finish(db)
    return row_response(inventory_crud.get_balance(db,data.material_id))
