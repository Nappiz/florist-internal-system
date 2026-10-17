from fastapi import HTTPException
from crud import purchases_crud
from use_cases.purchases.response import response


def get(db,actor,identity):
    row=purchases_crud.get(db,identity)
    if row is None: raise HTTPException(404,'Pembelian tidak ditemukan.')
    return response(db,row)
