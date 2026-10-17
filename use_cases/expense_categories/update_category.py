from fastapi import HTTPException
from crud import expense_categories_crud as crud
from use_cases.expense_categories.create_category import validate_category
from use_cases.operational_expenses.access import require_superadmin
from use_cases.common.persistence import finish
from use_cases.audit.record import record


def update_category(db,actor,category_id,data):
    require_superadmin(actor)
    row=crud.get(db,category_id,lock=True)
    if row is None: raise HTTPException(404,'Kategori tidak ditemukan.')
    values=data.model_dump(exclude_unset=True); validate_category(values)
    for key,value in values.items(): setattr(row,key,value)
    record(db,actor,'update','expense_category',row.id,{'fields':list(values)})
    finish(db)
    return row
