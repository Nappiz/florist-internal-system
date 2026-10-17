from fastapi import HTTPException
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.custom_bouquets.estimate import estimate
from use_cases.custom_bouquets.save_configuration import save_configuration
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from schemas.custom_bouquet_schema import BouquetCreate,BouquetUpdate
from use_cases.custom_bouquets.configuration_input import configuration_input

def update_bouquet(db,actor,identity,data):
    row=get_bouquet(db,identity,lock=True)
    if row.status!="draft": raise HTTPException(409,"Hanya konfigurasi draft dapat diubah.")
    if isinstance(data,BouquetUpdate):
        changes=data.model_dump(exclude_unset=True)
        if not changes or any(changes.get(key,"unset") is None for key in ("flowers","options","additional_materials","personalization")):
            raise HTTPException(422,"Isi perubahan valid; komposisi tidak boleh null.")
        data=BouquetCreate(**{**configuration_input(row).model_dump(),**changes})
    save_configuration(db,actor,row,data,estimate(db,data))
    record(db,actor,"update","custom_bouquet",row.id)
    finish(db)
    return row
