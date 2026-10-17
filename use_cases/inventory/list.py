from fastapi import HTTPException
from sqlalchemy import func,select
from models.material_model import Material
from models.inventory_balance_model import InventoryBalance
from use_cases.inventory.get import get


def list_rows(db,actor,query,low_stock=False):
    statement=select(Material.id).join(InventoryBalance,InventoryBalance.material_id==Material.id)
    if query.material_id: statement=statement.where(Material.id==query.material_id)
    if query.q: statement=statement.where(Material.name.icontains(query.q,autoescape=True))
    if low_stock: statement=statement.where(Material.is_active.is_(True),InventoryBalance.quantity_on_hand<=Material.minimum_stock)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    ids=db.scalars(statement.order_by(Material.name,Material.id).limit(query.limit).offset(query.offset))
    return {'items':[get(db,actor,identity) for identity in ids],'total':total,'limit':query.limit,'offset':query.offset}
