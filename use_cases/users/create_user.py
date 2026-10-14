from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User
from schemas.auth_schema import AuthContext
from schemas.user_schema import UserCreate
from services.user_security import hash_password
from use_cases.users.validate_password import validate_password


def create_user(db: Session, actor: AuthContext, data: UserCreate) -> User:
    if not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat membuat user.")
    username = data.username.lower()
    if username == "superadmin":
        raise HTTPException(409, "Username tidak tersedia.")
    password = data.password.get_secret_value()
    validate_password(password)
    try:
        user = users_crud.add(db, User(username=username, password_hash=hash_password(password), is_superadmin=False))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username tidak tersedia.") from None
    db.refresh(user)
    return user
