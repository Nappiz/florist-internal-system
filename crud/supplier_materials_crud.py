from sqlalchemy import func,or_,select
from models.material_model import Material
from models.supplier_store_model import SupplierStore
from models.supplier_material_model import SupplierMaterial


def get(db,identity,lock=False):
    statement=select(SupplierMaterial).where(SupplierMaterial.id==identity)
    return db.scalar(statement.with_for_update() if lock else statement)


def list_rows(db,query):
    statement=select(SupplierMaterial).join(Material,Material.id==SupplierMaterial.material_id).join(SupplierStore,SupplierStore.id==SupplierMaterial.supplier_id)
    if query.q: statement=statement.where(or_(SupplierMaterial.listing_name.icontains(query.q,autoescape=True),Material.name.icontains(query.q,autoescape=True),SupplierStore.name.icontains(query.q,autoescape=True)))
    if query.is_active is not None: statement=statement.where(SupplierMaterial.is_active==query.is_active)
    if query.material_id: statement=statement.where(SupplierMaterial.material_id==query.material_id)
    if query.supplier_id: statement=statement.where(SupplierMaterial.supplier_id==query.supplier_id)
    if query.platform: statement=statement.where(SupplierStore.platform==query.platform)
    if query.category: statement=statement.where(Material.category==query.category)
    if query.min_price is not None: statement=statement.where(SupplierMaterial.listed_price>=query.min_price)
    if query.max_price is not None: statement=statement.where(SupplierMaterial.listed_price<=query.max_price)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    ordering=SupplierMaterial.created_at.desc()
    if query.sort=='price_asc': ordering=SupplierMaterial.listed_price.asc()
    if query.sort=='unit_price_asc': ordering=(SupplierMaterial.listed_price/SupplierMaterial.quantity_in_base_unit).asc()
    return list(db.scalars(statement.order_by(ordering,SupplierMaterial.id).limit(query.limit).offset(query.offset))),total


def add(db,row):
    db.add(row)
    return row
