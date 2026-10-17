from fastapi import HTTPException


def validate(db,values,row=None):
    if any(values[key] is None for key in {'name','platform','is_active'} & values.keys()): raise HTTPException(422,'Field wajib tidak boleh null.')
    if values.get('shop_url') and '@' in values['shop_url'].split('://',1)[-1].split('/',1)[0]: raise HTTPException(422,'URL tidak boleh memuat credential.')
