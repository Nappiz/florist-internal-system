from crud import flowers_crud
from use_cases.flowers.get_flower import get_flower


def list_flowers(db, filters):
    rows, total = flowers_crud.list_page(db, filters)
    return {"items": [get_flower(db, row.id) for row in rows], "total": total, "limit": filters.limit, "offset": filters.offset}

