from crud import products_crud
from use_cases.products.get_product import get_product


def list_products(db, filters):
    rows, total = products_crud.list_page(db, filters)
    return {"items": [get_product(db, row.id) for row in rows], "total": total, "limit": filters.limit, "offset": filters.offset}

