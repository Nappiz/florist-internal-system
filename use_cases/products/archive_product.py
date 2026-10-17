from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException

from crud import products_crud
from use_cases.audit.record import record
from use_cases.common.persistence import finish


def archive_product(db, actor, entity_id):
    entity = products_crud.get(db, UUID(str(entity_id)), lock=True)
    if entity is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    entity.is_active = False
    entity.updated_at = datetime.now(UTC)
    record(db, actor, "archive", "product", entity.id)
    finish(db)

