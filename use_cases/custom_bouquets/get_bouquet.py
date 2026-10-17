from fastapi import HTTPException
from crud import custom_bouquets_crud

def get_bouquet(db,identity,*,lock=False):
    row=custom_bouquets_crud.get(db,identity,lock=lock)
    if row is None: raise HTTPException(404,"Konfigurasi buket tidak ditemukan.")
    return row
