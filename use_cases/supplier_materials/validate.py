from datetime import UTC,datetime
from decimal import Decimal,localcontext
from fastapi import HTTPException
from models.material_model import Material
from models.supplier_store_model import SupplierStore
from use_cases.common.validation import require_active


def validate(db,values,row=None):
    if any(values[key] is None for key in {'material_id','supplier_id','listing_name','package_quantity','package_unit','quantity_in_base_unit','listed_price','is_active'} & values.keys()): raise HTTPException(422,'Field wajib tidak boleh null.')
    require_active(db,SupplierStore,values.get('supplier_id',getattr(row,'supplier_id',None)))
    require_active(db,Material,values.get('material_id',getattr(row,'material_id',None)))
    with localcontext() as context:
        context.prec=60
        cost=Decimal(values.get('listed_price',getattr(row,'listed_price',0)))/Decimal(values.get('quantity_in_base_unit',getattr(row,'quantity_in_base_unit',1)))
        if cost>Decimal('9999999999999999.99999999'): raise HTTPException(422,'Harga per satuan dasar di luar batas biaya inventory.')
    if 'last_checked_at' in values:
        value=values['last_checked_at']
        if value is None: values['last_checked_at']=datetime.now(UTC)
        elif value.tzinfo is None or value>datetime.now(UTC): raise HTTPException(422,'Waktu pengecekan harus berzona waktu dan tidak di masa depan.')
    if values.get('listing_url') and '@' in values['listing_url'].split('://',1)[-1].split('/',1)[0]: raise HTTPException(422,'URL tidak boleh memuat credential.')
