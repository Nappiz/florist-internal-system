from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User
from schemas.auth_schema import AuthContext


def list_users(db: Session, actor: AuthContext, limit: int, offset: int) -> list[User]:
    if not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat melihat daftar user.")
    return users_crud.list_users(db, limit, offset)
