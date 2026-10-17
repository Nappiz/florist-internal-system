from fastapi import HTTPException
from crud import bouquet_options_crud
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.audit.record import record
from use_cases.common.persistence import finish

def archive_option(db,actor,identity):
    require_superadmin(actor)
    row=bouquet_options_crud.get(db,identity,lock=True)
    if row is None: raise HTTPException(404,"Opsi buket tidak ditemukan.")
    row.is_active=False
    record(db,actor,"archive","bouquet_option",row.id)
    finish(db)
