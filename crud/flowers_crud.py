from sqlalchemy import delete, func, or_, select

from models.flower_model import Flower
from models.flower_material_model import FlowerMaterial


def get(db, entity_id, *, lock=False):
    statement = select(Flower).where(Flower.id == entity_id)
    if lock:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_page(db, filters):
    statement = select(Flower)
    if filters.q:
        pattern = "%" + filters.q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        statement = statement.where(or_(Flower.name.ilike(pattern, escape="\\"), Flower.sku.ilike(pattern, escape="\\")))
    if filters.category is not None:
        statement = statement.where(Flower.category == filters.category)
    if filters.is_active is not None:
        statement = statement.where(Flower.is_active == filters.is_active)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    ordering = {"newest": Flower.created_at.desc(), "name": Flower.name, "sku": Flower.sku, "price_asc": Flower.selling_price, "price_desc": Flower.selling_price.desc()}
    rows = db.scalars(statement.order_by(ordering[filters.sort], Flower.id).limit(filters.limit).offset(filters.offset)).all()
    return rows, total


def add(db, entity):
    db.add(entity)
    return entity


def materials(db, entity_id):
    return db.scalars(select(FlowerMaterial).where(FlowerMaterial.flower_id == entity_id).order_by(FlowerMaterial.material_id)).all()


def clear_materials(db, entity_id):
    db.execute(delete(FlowerMaterial).where(FlowerMaterial.flower_id == entity_id))


