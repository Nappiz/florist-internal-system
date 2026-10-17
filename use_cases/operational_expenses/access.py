from datetime import UTC, datetime, timedelta, timezone
from fastapi import HTTPException
from crud import operational_expenses_crud as crud, expense_categories_crud


def require_superadmin(actor):
    if not actor.user.is_superadmin:
        raise HTTPException(403, 'Hanya superadmin yang dapat memfinalisasi keuangan.')


def get_authorized(db, actor, identity, lock=False):
    row=crud.get(db,identity,lock)
    if row is None or (not actor.user.is_superadmin and row.created_by!=actor.user.id):
        raise HTTPException(404,'Expense tidak ditemukan.')
    return row


def require_draft(row):
    if row.status!='draft':
        raise HTTPException(409,'Hanya draft expense yang dapat diubah.')


def validate_values(db, values):
    for key in ('title','category_id','expense_date','amount'):
        if key in values and values[key] is None:
            raise HTTPException(422,'Field wajib tidak boleh null.')
    if 'expense_date' in values and values['expense_date']>datetime.now(timezone(timedelta(hours=7))).date():
        raise HTTPException(422,'Tanggal expense tidak boleh di masa depan.')
    if 'category_id' in values:
        category=expense_categories_crud.get(db,values['category_id'],lock=True)
        if category is None or not category.is_active:
            raise HTTPException(409,'Kategori harus aktif.')
    if 'amount' in values and (values['amount']<=0 or values['amount']>999999999999999):
        raise HTTPException(422,'Nominal expense harus positif.')


def validate_filters(filters):
    if filters.date_from and filters.date_to and filters.date_from>filters.date_to:
        raise HTTPException(422,'Rentang tanggal tidak valid.')
    if filters.amount_min is not None and filters.amount_max is not None and filters.amount_min>filters.amount_max:
        raise HTTPException(422,'Rentang nominal tidak valid.')
