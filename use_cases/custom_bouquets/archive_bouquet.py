from datetime import UTC,datetime
from fastapi import HTTPException
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.audit.record import record
from use_cases.common.persistence import finish

def archive_bouquet(db,actor,identity):
    row=get_bouquet(db,identity,lock=True)
    if row.status=="archived": raise HTTPException(409,"Konfigurasi sudah diarsipkan.")
    row.status="archived"
    row.updated_by=actor.user.id
    row.updated_at=datetime.now(UTC)
    record(db,actor,"archive","custom_bouquet",row.id)
    finish(db)
    return row
