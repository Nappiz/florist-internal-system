from crud import custom_bouquets_crud

def list_bouquets(db,filters):
    rows,total=custom_bouquets_crud.list_page(db,filters)
    return {"items":rows,"total":total,"limit":filters.limit,"offset":filters.offset}
