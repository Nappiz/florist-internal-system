from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import users_crud
from models.user_model import User


def protect_last_superadmin(db: Session, user: User, role: str, is_active: bool) -> None:
    # Administration routes hold the transaction advisory lock before actor locks.
    if user.role == "superadmin" and user.is_active and (role != "superadmin" or not is_active):
        if users_crud.count_active_superadmins(db) <= 1:
            raise HTTPException(403, "Minimal satu superadmin aktif harus tersedia.")
