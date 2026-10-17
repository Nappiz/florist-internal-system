from sqlalchemy import func,or_,select
from models.material_model import Material


def get(db,identity,lock=False):
    statement=select(Material).where(Material.id==identity)
    return db.scalar(statement.with_for_update() if lock else statement)


def list_rows(db,query):
    statement=select(Material)
    if query.q: statement=statement.where(or_(Material.name.icontains(query.q,autoescape=True),Material.sku.icontains(query.q,autoescape=True)))
    if query.is_active is not None: statement=statement.where(Material.is_active==query.is_active)
    if query.category: statement=statement.where(Material.category==query.category)
    if query.base_unit: statement=statement.where(Material.base_unit==query.base_unit)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    return list(db.scalars(statement.order_by(Material.name,Material.id).limit(query.limit).offset(query.offset))),total


def add(db,row):
    db.add(row)
    return row
