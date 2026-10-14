from datetime import datetime

from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.login_throttle_model import LoginThrottle


def reserve_attempt(db: Session, key: str, now: datetime, cutoff: datetime) -> int:
    expired = LoginThrottle.window_started <= cutoff
    statement = (
        insert(LoginThrottle)
        .values(bucket_key=key, attempts=1, window_started=now)
        .on_conflict_do_update(
            index_elements=[LoginThrottle.bucket_key],
            set_={
                "attempts": case((expired, 1), else_=LoginThrottle.attempts + 1),
                "window_started": case((expired, now), else_=LoginThrottle.window_started),
            },
        )
        .returning(LoginThrottle.attempts)
    )
    return db.scalar(statement)


def delete_expired(db: Session, cutoff: datetime) -> None:
    expired_keys = (
        select(LoginThrottle.bucket_key)
        .where(LoginThrottle.window_started <= cutoff)
        .limit(1000)
        .with_for_update(skip_locked=True)
    )
    db.execute(delete(LoginThrottle).where(LoginThrottle.bucket_key.in_(expired_keys)))
