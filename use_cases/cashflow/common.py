from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from crud import cash_accounts_crud, cashflow_crud
from models.cash_operation_model import CashOperation
from models.cash_transaction_model import CashTransaction


def require_superadmin(actor):
    user = getattr(actor, 'user', actor)
    if not user or not getattr(user, 'is_active', True) or not user.is_superadmin:
        raise HTTPException(403, 'Keuangan hanya dapat diakses Superadmin.')
    return user


def today():
    return datetime.now(ZoneInfo('Asia/Jakarta')).date()


def validate_date(value, account=None):
    if value is None or value > today():
        raise HTTPException(422, 'Tanggal wajib dan tidak boleh di masa depan.')
    if account is not None and value < account.opening_date:
        raise HTTPException(422, 'Tanggal tidak boleh sebelum tanggal awal rekening.')


def require_accounts(db, identities, transaction_date):
    accounts = cash_accounts_crud.lock_many(db, set(identities))
    if len(accounts) != len(set(identities)):
        raise HTTPException(404, 'Cash account tidak ditemukan.')
    for account in accounts:
        if not account.is_active:
            raise HTTPException(409, 'Cash account tidak aktif.')
        validate_date(transaction_date, account)
    return {account.id: account for account in accounts}


def operation(db, actor, kind, data, extra=None):
    payload = data.model_dump(mode='json') | (extra or {})
    existing = cashflow_crud.operation(db, data.operation_key)
    if existing is None:
        candidate = CashOperation(operation_key=data.operation_key, kind=kind, request_payload=payload, created_by=actor.user.id)
        try:
            db.add(candidate)
            db.flush()
            return candidate
        except IntegrityError:
            db.rollback()
            existing = cashflow_crud.operation(db, data.operation_key)
            if existing is None:
                raise HTTPException(409, 'Operasi keuangan bertentangan dengan data tersimpan.') from None
    if existing.kind != kind or existing.request_payload != payload:
        raise HTTPException(409, 'Operation key sudah digunakan dengan isi berbeda.')
    return existing


def movement(db, actor, *, account_id, transaction_date, direction, amount, category, source_type, source_id=None, reason=None, operation_key=None, reversal_of_id=None):
    identity = uuid4()
    row = CashTransaction(id=identity, transaction_number='CSH-' + identity.hex, cash_account_id=account_id, transaction_date=transaction_date, direction=direction, amount=amount, category=category, source_type=source_type, source_id=source_id or identity, description=reason, operation_key=operation_key, reversal_of_id=reversal_of_id, created_by=actor.user.id)
    db.add(row)
    return row


def report_query(query):
    values = {}
    if query.period:
        if query.date_from or query.date_to:
            raise HTTPException(422, 'Pilih periode atau tanggal khusus.')
        day = today()
        start = day if query.period == 'today' else day - timedelta(days=day.weekday()) if query.period == 'this_week' else day.replace(day=1)
        values = {'date_from': start, 'date_to': day}
    result = query.model_copy(update=values)
    if result.date_from and result.date_to and result.date_from > result.date_to:
        raise HTTPException(422, 'Tanggal awal melebihi tanggal akhir.')
    return result
