from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select


def require_active(db, model, identity):
    row = db.scalar(select(model).where(model.id == identity).with_for_update())
    if row is None:
        raise HTTPException(404, 'Referensi tidak ditemukan.')
    if not row.is_active:
        raise HTTPException(409, 'Referensi sudah diarsipkan.')
    return row


def money(value):
    value = Decimal(value)
    if not value.is_finite() or value < 0 or value > Decimal('999999999999999'):
        raise HTTPException(422, 'Nilai rupiah di luar batas.')
    return int(value.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def quantity(value):
    value = Decimal(value)
    if not value.is_finite() or value <= 0 or value > Decimal('999999999999.999999') or value != value.quantize(Decimal('.000001')):
        raise HTTPException(422, 'Kuantitas harus positif dengan maksimal enam desimal.')
    return value
