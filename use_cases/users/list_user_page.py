from fastapi import HTTPException
from crud import users_crud


def list_user_page(db,actor,query):
    if not actor.user.is_superadmin: raise HTTPException(403,'Hanya superadmin dapat melihat daftar user.')
    rows,total=users_crud.list_page(db,query)
    return {'items':rows,'total':total,'limit':query.limit,'offset':query.offset}
