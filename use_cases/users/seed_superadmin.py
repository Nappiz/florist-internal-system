from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User
from schemas.user_schema import UserCreate
from services.user_security import hash_password
from use_cases.users.validate_password import validate_password


def seed_superadmin(db: Session, password: str, *, full_name: str = "Superadmin", email: str = "superadmin@legacy.invalid") -> User:
    users_crud.lock_administration(db)
    existing = users_crud.get_superadmin(db)
    if existing is not None:
        return existing
    validate_password(password)
    if users_crud.get_by_username(db, "superadmin") is not None:
        raise HTTPException(409, "Username seed sudah dipakai; tidak akan meningkatkan role user existing.")
    profile = UserCreate(username="superadmin", password=password, full_name=full_name, email=email, role="superadmin")
    try:
        user = users_crud.add(db, User(username="superadmin", password_hash=hash_password(password),
            full_name=profile.full_name, email=profile.email, role="superadmin", is_superadmin=True))
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = users_crud.get_superadmin(db)
        if existing is not None:
            return existing
        raise HTTPException(409, "Seed superadmin gagal karena konflik akun.") from None
    db.refresh(user)
    return user
