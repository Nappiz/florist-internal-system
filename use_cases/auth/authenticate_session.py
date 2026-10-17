import re
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, users_crud
from schemas.auth_schema import AuthContext
from services.user_security import csrf_token_for, hash_token


def authenticate_session(db: Session, token: str | None) -> AuthContext:
    if token is None or re.fullmatch(r"[A-Za-z0-9_-]{43}", token) is None:
        raise HTTPException(401, "Login diperlukan.")
    now = datetime.now(UTC)
    digest = hash_token(token)
    candidate = auth_sessions_crud.get_candidate(db, digest, now)
    if candidate is None:
        raise HTTPException(401, "Session tidak valid atau sudah berakhir.")
    # Lock order is always user, then session. Re-read after locking the user so
    # concurrent logout/password updates cannot resurrect a stale session.
    user = users_crud.get_by_id(db, candidate.user_id)
    session = auth_sessions_crud.get_active(db, digest, datetime.now(UTC))
    if user is None or not user.is_active or session is None or session.credential_version != user.credential_version:
        raise HTTPException(401, "Session tidak valid atau sudah berakhir.")
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        raise HTTPException(401, "Session tidak valid atau sudah berakhir.")
    return AuthContext(user=user, session=session, csrf_token=csrf_token_for(token))
