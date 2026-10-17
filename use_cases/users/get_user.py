from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User
from schemas.auth_schema import AuthContext


def get_user(db: Session, actor: AuthContext, user_id: UUID) -> User:
    if not actor.user.is_superadmin and actor.user.id != user_id:
        raise HTTPException(403, "Tidak diizinkan mengakses user lain.")
    user = users_crud.read_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User tidak ditemukan.")
    return user
