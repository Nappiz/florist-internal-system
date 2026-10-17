from fastapi import HTTPException
from crud import bouquet_options_crud
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.bouquet_options.save_option import save_option
from use_cases.bouquet_options.option_response import option_response
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from schemas.bouquet_option_schema import BouquetOptionCreate,BouquetOptionUpdate

def update_option(db,actor,identity,data):
    require_superadmin(actor)
    row=bouquet_options_crud.get(db,identity,lock=True)
    if row is None: raise HTTPException(404,"Opsi buket tidak ditemukan.")
    if isinstance(data,BouquetOptionUpdate):
        changes=data.model_dump(exclude_unset=True)
        required={"name","option_group","selling_price","min_quantity","max_quantity","requires_materials","is_active","materials"}
        if not changes or any(changes[key] is None for key in required & changes.keys()):
            raise HTTPException(422,"Isi perubahan valid; field wajib tidak boleh null.")
        current=option_response(db,row).model_dump(exclude={"id"})
        data=BouquetOptionCreate(**{**current,**changes})
    save_option(db,row,data)
    record(db,actor,"update","bouquet_option",row.id)
    finish(db)
    return option_response(db,row)
