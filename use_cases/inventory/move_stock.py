from collections import defaultdict
from decimal import Decimal,ROUND_HALF_UP,localcontext
from uuid import UUID
from fastapi import HTTPException
from crud import inventory_crud
from models.inventory_movement_model import InventoryMovement


def move_stock(db,actor,changes,reference_type,reference_id):
    with localcontext() as context:
        context.prec=60
        return _move_stock(db,actor,changes,reference_type,reference_id)


def _move_stock(db,actor,changes,reference_type,reference_id):
    grouped={}
    for change in changes:
        identity=UUID(str(change['material_id']))
        delta=Decimal(change['quantity_delta'])
        if not delta.is_finite() or delta==0 or abs(delta)>Decimal('999999999999.999999') or delta!=delta.quantize(Decimal('.000001')):
            raise HTTPException(422,'Kuantitas stok tidak valid.')
        cost=Decimal(change.get('unit_cost',0))
        if not cost.is_finite() or cost<0 or cost>Decimal('9999999999999999.99999999'): raise HTTPException(422,'Biaya unit tidak valid.')
        row=grouped.setdefault(identity,{'delta':Decimal(0),'value':Decimal(0),'notes':change.get('notes')})
        if row['delta'] and (row['delta']>0)!=(delta>0): raise HTTPException(422,'Arah pergerakan material bertentangan.')
        row['delta']+=delta
        row['value']+=delta*cost
    balances={row.material_id:row for row in inventory_crud.lock_balances(db,sorted(grouped,key=str))}
    if len(balances)!=len(grouped): raise HTTPException(409,'Saldo awal material belum tersedia.')
    total=Decimal(0)
    # Validate every row before applying any mutation.
    for identity,data in grouped.items():
        balance=balances[identity]
        event=f'{reference_type}:{reference_id}:{identity}'
        if inventory_crud.get_event(db,event): raise HTTPException(409,'Pergerakan stok sudah diproses.')
        if balance.quantity_on_hand+data['delta']<0: raise HTTPException(409,{'message':'Stok material tidak mencukupi.','material_id':str(identity),'available':str(balance.quantity_on_hand),'required':str(-data['delta'])})
        if balance.quantity_on_hand+data['delta']>Decimal('999999999999.999999'): raise HTTPException(422,'Saldo stok di luar batas.')
    for identity,data in grouped.items():
        balance=balances[identity]
        delta=data['delta']
        cost=balance.average_unit_cost
        if delta>0:
            cost=(data['value']/delta).quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP)
            balance.average_unit_cost=((balance.quantity_on_hand*balance.average_unit_cost+data['value'])/(balance.quantity_on_hand+delta)).quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP)
            balance.has_received_cost=True
        else: total+=(-delta)*cost
        balance.quantity_on_hand+=delta
        db.add(InventoryMovement(material_id=identity,event_key=f'{reference_type}:{reference_id}:{identity}',movement_type='ADJUSTMENT' if reference_type=='adjustment' else ('IN' if delta>0 else 'OUT'),quantity_delta=delta,unit_cost_snapshot=cost,reference_type=reference_type,reference_id=reference_id,notes=data['notes'],created_by=actor.user.id))
    return total.quantize(Decimal('.00000001'),rounding=ROUND_HALF_UP)
