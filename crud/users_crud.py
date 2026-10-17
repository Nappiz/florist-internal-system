from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from models.user_model import User


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username).with_for_update().execution_options(populate_existing=True))


def get_by_login(db: Session, identifier: str) -> User | None:
    return db.scalar(select(User).where(or_(User.username == identifier, func.lower(User.email) == identifier)).with_for_update().execution_options(populate_existing=True))


def get_login_username(db: Session, identifier: str) -> str | None:
    return db.scalar(select(User.username).where(or_(User.username == identifier, func.lower(User.email) == identifier)))


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id).with_for_update().execution_options(populate_existing=True))


def read_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_superadmin(db: Session) -> User | None:
    return db.scalar(select(User).where(User.role == "superadmin").order_by(User.created_at, User.id).limit(1).with_for_update())


def lock_administration(db: Session) -> None:
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(762411892001)"))


def count_active_superadmins(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.role == "superadmin", User.is_active.is_(True)))


def list_users(db: Session, limit: int, offset: int) -> list[User]:
    return list(db.scalars(select(User).order_by(User.username).limit(limit).offset(offset)))


def list_page(db,query):
    statement=select(User)
    if query.q: statement=statement.where(or_(*(column.icontains(query.q,autoescape=True) for column in (User.username,User.full_name,User.email))))
    if query.role: statement=statement.where(User.role==query.role)
    if query.is_active is not None: statement=statement.where(User.is_active==query.is_active)
    total=db.scalar(select(func.count()).select_from(statement.subquery()))
    return list(db.scalars(statement.order_by(User.username,User.id).limit(query.limit).offset(query.offset))),total


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
