from sqlalchemy import select,delete,func
from models.bouquet_option_model import BouquetOption
from models.bouquet_option_material_model import BouquetOptionMaterial

def get(db,identity,*,lock=False):
    query=select(BouquetOption).where(BouquetOption.id==identity)
    return db.scalar(query.with_for_update() if lock else query)

def list_page(db,filters):
    query=select(BouquetOption)
    if filters.is_active is not None: query=query.where(BouquetOption.is_active==filters.is_active)
    if filters.option_group is not None: query=query.where(BouquetOption.option_group==filters.option_group)
    total=db.scalar(select(func.count()).select_from(query.subquery()))
    return db.scalars(query.order_by(BouquetOption.name,BouquetOption.id).limit(filters.limit).offset(filters.offset)).all(),total

def materials(db,identity):
    return db.scalars(select(BouquetOptionMaterial).where(BouquetOptionMaterial.bouquet_option_id==identity).order_by(BouquetOptionMaterial.material_id)).all()

def add(db,row):
    db.add(row)
    return row

def replace_materials(db,identity,rows):
    db.execute(delete(BouquetOptionMaterial).where(BouquetOptionMaterial.bouquet_option_id==identity))
    db.add_all(rows)
