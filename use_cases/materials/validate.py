from fastapi import HTTPException
from sqlalchemy import select
from use_cases.common.validation import quantity


def validate(db,values,row=None):
    required={'sku','name','base_unit','minimum_stock','is_active'}
    if any(values[key] is None for key in required & values.keys()): raise HTTPException(422,'Field wajib tidak boleh null.')
    if 'sku' in values: values['sku']=values['sku'].upper()
    if row and 'base_unit' in values and values['base_unit']!=row.base_unit:
        # Restrict once used in any recipe, offer or transaction: conversions then remain reliable.
        from models.supplier_material_model import SupplierMaterial
        from models.inventory_movement_model import InventoryMovement
        from models.purchase_item_model import PurchaseItem
        from models.flower_material_model import FlowerMaterial
        from models.product_material_model import ProductMaterial
        for model in (SupplierMaterial,InventoryMovement,PurchaseItem,FlowerMaterial,ProductMaterial):
            if db.scalar(select(model.id).where(model.material_id==row.id).limit(1)) is not None:
                raise HTTPException(409,'Satuan material yang sudah digunakan tidak dapat diubah.')
    for name in ('image_url',):
        if values.get(name) and '@' in values[name].split('://',1)[-1].split('/',1)[0]: raise HTTPException(422,'URL tidak boleh memuat credential.')
