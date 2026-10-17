from crud import bouquet_options_crud
from use_cases.bouquet_options.option_response import option_response

def list_options(db,filters):
    rows,total=bouquet_options_crud.list_page(db,filters)
    return {"items":[option_response(db,row) for row in rows],"total":total,"limit":filters.limit,"offset":filters.offset}
