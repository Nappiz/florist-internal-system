from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.auth_session_model import AuthSession


def add(db: Session, session: AuthSession) -> None:
    db.add(session)
    db.flush()


def get_candidate(db: Session, token_hash: str, now: datetime) -> AuthSession | None:
    return db.scalar(
        select(AuthSession)
        .where(AuthSession.token_hash == token_hash, AuthSession.expires_at > now)
    )


def get_active(db: Session, token_hash: str, now: datetime) -> AuthSession | None:
    return db.scalar(
        select(AuthSession)
        .where(AuthSession.token_hash == token_hash, AuthSession.expires_at > now)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def revoke_user_sessions(db: Session, user_id: UUID) -> None:
    db.execute(delete(AuthSession).where(AuthSession.user_id == user_id))


def revoke_session(db: Session, session_id: UUID) -> None:
    db.execute(delete(AuthSession).where(AuthSession.id == session_id))


def delete_expired(db: Session, now: datetime) -> None:
    expired_ids = select(AuthSession.id).where(AuthSession.expires_at <= now).limit(1000).with_for_update(skip_locked=True)
    db.execute(delete(AuthSession).where(AuthSession.id.in_(expired_ids)))
