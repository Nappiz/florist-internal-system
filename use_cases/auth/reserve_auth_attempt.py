from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import login_throttles_crud
from services.user_security import hash_token


def reserve_auth_attempt(db: Session, username: str, client_ip: str) -> None:
    now = datetime.now(UTC)
    cutoff = now - timedelta(minutes=15)
    ip_attempts = login_throttles_crud.reserve_attempt(db, hash_token("ip:" + client_ip), now, cutoff)
    user_attempts = login_throttles_crud.reserve_attempt(db, hash_token("username:" + username), now, cutoff)
    if ip_attempts > 30 or user_attempts > 5:
        db.commit()
        raise HTTPException(429, "Terlalu banyak percobaan autentikasi. Coba lagi nanti.", headers={"Retry-After": "900"})
