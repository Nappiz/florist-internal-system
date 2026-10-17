from fastapi import HTTPException
from crud import purchases_crud
from use_cases.common.response import row_response


def list_rows(db,actor,query):
    if query.date_from and query.date_to and query.date_from>query.date_to: raise HTTPException(422,'Rentang tanggal tidak valid.')
    if query.min_total is not None and query.max_total is not None and query.min_total>query.max_total: raise HTTPException(422,'Rentang nominal tidak valid.')
    rows,total=purchases_crud.list_rows(db,query)
    names_by_purchase={}
    for purchase_id,name in purchases_crud.list_item_names(db,[row.id for row in rows]):
        names_by_purchase.setdefault(purchase_id,[]).append(name)
    items=[{'item_names':names_by_purchase.get(row.id,[]),**row_response(row)} for row in rows]
    return {'items':items,'total':total,'limit':query.limit,'offset':query.offset}
