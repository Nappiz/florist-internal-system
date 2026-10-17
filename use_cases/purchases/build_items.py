from decimal import Decimal,localcontext
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select
from models.material_model import Material
from models.supplier_material_model import SupplierMaterial
from models.purchase_item_model import PurchaseItem
from use_cases.common.validation import require_active,money,quantity


def build_items(db,purchase,items):
    result=[]
    for data in sorted(items,key=lambda item:str(item.material_id)):
        material=require_active(db,Material,data.material_id)
        unit_price=data.unit_price
        quantity_base=data.quantity_base
        if data.supplier_listing_id:
            listing=require_active(db,SupplierMaterial,data.supplier_listing_id)
            if listing.material_id!=material.id or listing.supplier_id!=purchase.supplier_id: raise HTTPException(422,'Listing tidak sesuai material dan supplier pembelian.')
            converted=quantity(data.quantity*listing.quantity_in_base_unit)
            if quantity_base is not None and quantity_base!=converted: raise HTTPException(422,'Kuantitas dasar harus sesuai konversi listing.')
            quantity_base=converted
            if unit_price is None: unit_price=listing.listed_price
        elif quantity_base is None:
            quantity_base=data.quantity
        if unit_price is None: raise HTTPException(422,'Harga aktual diperlukan tanpa listing referensi.')
        subtotal=money(data.quantity*Decimal(unit_price))
        with localcontext() as context:
            context.prec=60
            if Decimal(subtotal)/quantity_base>Decimal('9999999999999999.99999999'): raise HTTPException(422,'Biaya unit material di luar batas inventory.')
        result.append(PurchaseItem(id=uuid4(),purchase_id=purchase.id,material_id=material.id,supplier_listing_id=data.supplier_listing_id,material_name_snapshot=material.name,base_unit_snapshot=material.base_unit,quantity=data.quantity,quantity_base=quantity(quantity_base),unit_price=unit_price,subtotal=subtotal))
    return result
