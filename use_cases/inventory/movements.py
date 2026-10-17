from fastapi import HTTPException
from sqlalchemy import func,select
from models.inventory_movement_model import InventoryMovement
from use_cases.common.response import row_response


def movements(db,actor,query):
    if query.date_from and query.date_to and query.date_from>query.date_to: raise HTTPException(422,'Rentang tanggal tidak valid.')
    statement=select(InventoryMovement)
    if query.material_id: statement=statement.where(InventoryMovement.material_id==query.material_id)
    if query.date_from: statement=statement.where(InventoryMovement.created_at>=query.date_from)
    if query.date_to: statement=statement.where(InventoryMovement.created_at<=query.date_to)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    rows=db.scalars(statement.order_by(InventoryMovement.created_at.desc(),InventoryMovement.id).limit(query.limit).offset(query.offset))
    return {'items':[row_response(row) for row in rows],'total':total,'limit':query.limit,'offset':query.offset}
