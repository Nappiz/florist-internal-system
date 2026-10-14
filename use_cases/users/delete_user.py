from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import users_crud
from schemas.auth_schema import AuthContext


def delete_user(db: Session, actor: AuthContext, user_id: UUID) -> None:
    if not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat menghapus user.")
    user = users_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User tidak ditemukan.")
    if user.is_superadmin:
        raise HTTPException(403, "Akun superadmin tidak boleh dihapus.")
    users_crud.delete(db, user)
    db.commit()
