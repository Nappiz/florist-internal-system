from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def finish(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Data bertentangan dengan referensi, nilai unik, atau batas database.') from None


def flush(db):
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Data bertentangan dengan referensi, nilai unik, atau batas database.') from None
