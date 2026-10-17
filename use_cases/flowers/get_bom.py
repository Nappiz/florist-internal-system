from uuid import UUID

from fastapi import HTTPException

from crud import flowers_crud


def get_bom(db, entity_id):
    entity_id = UUID(str(entity_id))
    if flowers_crud.get(db, entity_id) is None:
        raise HTTPException(404, "Bunga tidak ditemukan.")
    return {
        "materials": [{"material_id": row.material_id, "quantity_required": row.quantity_required, "unit": row.unit} for row in flowers_crud.materials(db, entity_id)],
    }

