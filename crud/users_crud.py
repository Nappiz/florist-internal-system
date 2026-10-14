from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user_model import User


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username).with_for_update())


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id).with_for_update())


def get_superadmin(db: Session) -> User | None:
    return db.scalar(select(User).where(User.is_superadmin.is_(True)).with_for_update())


def list_users(db: Session, limit: int, offset: int) -> list[User]:
    return list(db.scalars(select(User).order_by(User.username).limit(limit).offset(offset)))


def add(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user


def update(db: Session, user: User, values: dict) -> User:
    for field, value in values.items():
        setattr(user, field, value)
    db.flush()
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.flush()
