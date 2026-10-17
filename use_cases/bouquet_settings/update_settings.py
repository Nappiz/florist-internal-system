from fastapi import HTTPException
from crud import bouquet_settings_crud
from models.bouquet_setting_model import BouquetSetting
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.audit.record import record
from use_cases.common.persistence import finish

def update_settings(db,actor,data):
    require_superadmin(actor)
    if data.min_stems>data.max_stems: raise HTTPException(422,"Batas minimum tangkai melebihi maksimum.")
    row=bouquet_settings_crud.get(db,lock=True)
    if row is None: row=bouquet_settings_crud.add(db,BouquetSetting(id=1,pricing_version=0))
    for key,value in data.model_dump().items(): setattr(row,key,value)
    row.pricing_version+=1
    record(db,actor,"update","bouquet_settings",None,{"pricing_version":row.pricing_version})
    finish(db)
    return row
