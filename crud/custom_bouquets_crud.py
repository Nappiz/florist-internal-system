from sqlalchemy import select,delete,func
from models.custom_bouquet_model import CustomBouquet
from models.custom_bouquet_flower_model import CustomBouquetFlower
from models.custom_bouquet_option_model import CustomBouquetOption
from models.custom_bouquet_material_model import CustomBouquetMaterial

def get(db,identity,*,lock=False):
    query=select(CustomBouquet).where(CustomBouquet.id==identity)
    return db.scalar(query.with_for_update() if lock else query)

def list_page(db,filters):
    query=select(CustomBouquet)
    if filters.status is not None: query=query.where(CustomBouquet.status==filters.status)
    if filters.q:
        pattern="%"+filters.q.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")+"%"
        query=query.where(CustomBouquet.name.ilike(pattern,escape="\\"))
    total=db.scalar(select(func.count()).select_from(query.subquery()))
    return db.scalars(query.order_by(CustomBouquet.created_at.desc(),CustomBouquet.id).limit(filters.limit).offset(filters.offset)).all(),total

def add(db,row):
    db.add(row)
    return row

def components(db,identity,model):
    return db.scalars(select(model).where(model.custom_bouquet_id==identity)).all()

def replace_components(db,identity,flowers,options,materials):
    for model,rows in ((CustomBouquetFlower,flowers),(CustomBouquetOption,options),(CustomBouquetMaterial,materials)):
        db.execute(delete(model).where(model.custom_bouquet_id==identity))
        db.add_all(rows)
