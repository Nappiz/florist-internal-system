from sqlalchemy import delete, func, or_, select

from models.product_model import Product
from models.product_material_model import ProductMaterial
from models.product_flower_model import ProductFlower


def get(db, entity_id, *, lock=False):
    statement = select(Product).where(Product.id == entity_id)
    if lock:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_page(db, filters):
    statement = select(Product)
    if filters.q:
        pattern = "%" + filters.q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        statement = statement.where(or_(Product.name.ilike(pattern, escape="\\"), Product.sku.ilike(pattern, escape="\\")))
    if filters.category is not None:
        statement = statement.where(Product.category == filters.category)
    if filters.is_active is not None:
        statement = statement.where(Product.is_active == filters.is_active)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    ordering = {"newest": Product.created_at.desc(), "name": Product.name, "sku": Product.sku, "price_asc": Product.selling_price, "price_desc": Product.selling_price.desc()}
    rows = db.scalars(statement.order_by(ordering[filters.sort], Product.id).limit(filters.limit).offset(filters.offset)).all()
    return rows, total


def add(db, entity):
    db.add(entity)
    return entity


def materials(db, entity_id):
    return db.scalars(select(ProductMaterial).where(ProductMaterial.product_id == entity_id).order_by(ProductMaterial.material_id)).all()


def clear_materials(db, entity_id):
    db.execute(delete(ProductMaterial).where(ProductMaterial.product_id == entity_id))


def flowers(db, entity_id):
    return db.scalars(select(ProductFlower).where(ProductFlower.product_id == entity_id).order_by(ProductFlower.flower_id)).all()


def clear_flowers(db, entity_id):
    db.execute(delete(ProductFlower).where(ProductFlower.product_id == entity_id))

