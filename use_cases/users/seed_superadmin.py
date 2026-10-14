from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User
from services.user_security import hash_password
from use_cases.users.validate_password import validate_password


def seed_superadmin(db: Session, password: str) -> User:
    existing = users_crud.get_superadmin(db)
    if existing is not None:
        return existing
    validate_password(password)
    if users_crud.get_by_username(db, "superadmin") is not None:
        raise HTTPException(409, "Username seed sudah dipakai; tidak akan meningkatkan role user existing.")
    try:
        user = users_crud.add(db, User(username="superadmin", password_hash=hash_password(password), is_superadmin=True))
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = users_crud.get_superadmin(db)
        if existing is not None:
            return existing
        raise HTTPException(409, "Seed superadmin gagal karena konflik akun.") from None
    db.refresh(user)
    return user
