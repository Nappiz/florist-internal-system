import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, login_throttles_crud, users_crud
from models.auth_session_model import AuthSession
from schemas.auth_schema import LoginRequest, LoginResult
from services.user_security import DUMMY_PASSWORD_HASH, csrf_token_for, hash_token, verify_password
from use_cases.auth.reserve_auth_attempt import reserve_auth_attempt


def login(db: Session, data: LoginRequest, client_ip: str) -> LoginResult:
    now = datetime.now(UTC)
    cutoff = now - timedelta(minutes=15)
    username = data.username.lower()
    reserve_auth_attempt(db, username, client_ip)
    login_throttles_crud.delete_expired(db, cutoff)
    db.commit()

    password = data.password.get_secret_value()
    if not 1 <= len(password) <= 128:
        raise HTTPException(401, "Username atau password salah.")
    user = users_crud.get_by_username(db, username)
    valid = verify_password(user.password_hash if user else DUMMY_PASSWORD_HASH, password)
    if user is None or not valid:
        raise HTTPException(401, "Username atau password salah.")

    token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(hours=24)
    auth_sessions_crud.delete_expired(db, now)
    auth_sessions_crud.add(
        db,
        AuthSession(
            user_id=user.id,
            token_hash=hash_token(token),
            credential_version=user.credential_version,
            created_at=now,
            expires_at=expires_at,
        ),
    )
    db.commit()
    db.refresh(user)
    return LoginResult(user=user, token=token, csrf_token=csrf_token_for(token), expires_at=expires_at)
