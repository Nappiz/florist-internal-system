from uuid import UUID

from fastapi import HTTPException

from crud import products_crud


def get_bom(db, entity_id):
    entity_id = UUID(str(entity_id))
    if products_crud.get(db, entity_id) is None:
        raise HTTPException(404, "Produk tidak ditemukan.")
    return {
        "materials": [{"material_id": row.material_id, "quantity_required": row.quantity_required, "unit": row.unit} for row in products_crud.materials(db, entity_id)],
        "flowers": [{"flower_id": row.flower_id, "quantity_required": row.quantity_required} for row in products_crud.flowers(db, entity_id)],
    }

