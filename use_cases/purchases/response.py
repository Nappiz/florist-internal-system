from fastapi import HTTPException
from crud import purchases_crud
from use_cases.common.response import row_response


def require(db,identity):
    purchase=purchases_crud.get(db,identity,lock=True)
    if purchase is None: raise HTTPException(404,'Pembelian tidak ditemukan.')
    return purchase


def response(db,purchase):
    result=row_response(purchase)
    result['items']=[row_response(item) for item in purchases_crud.items(db,purchase.id)]
    result['payments']=[row_response(payment) for payment in purchases_crud.payments(db,purchase.id)]
    result['currency']='IDR'
    return result
