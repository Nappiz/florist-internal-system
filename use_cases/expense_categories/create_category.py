from fastapi import HTTPException
from crud import expense_categories_crud as crud
from models.expense_category_model import ExpenseCategory
from use_cases.operational_expenses.access import require_superadmin
from use_cases.common.persistence import finish,flush
from use_cases.audit.record import record


def validate_category(values):
    if any(key in values and values[key] is None for key in ('name','classification','is_active')):
        raise HTTPException(422,'Field wajib tidak boleh null.')
    name=values.get('name','').strip().casefold()
    if name in {'inventory','raw materials','materials','bahan baku','pembelian bahan baku','stok','inventory materials'}:
        raise HTTPException(422,'Pembelian material inventory harus dicatat melalui Purchases.')


def create_category(db,actor,data):
    require_superadmin(actor)
    values=data.model_dump(); validate_category(values)
    row=crud.add(db,ExpenseCategory(**values)); flush(db)
    record(db,actor,'create','expense_category',row.id)
    finish(db)
    return row
