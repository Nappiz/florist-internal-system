from fastapi import HTTPException
from crud import bouquet_options_crud
from use_cases.bouquet_options.option_response import option_response

def get_option(db,identity):
    row=bouquet_options_crud.get(db,identity)
    if row is None: raise HTTPException(404,"Opsi buket tidak ditemukan.")
    return option_response(db,row)
