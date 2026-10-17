from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, users_crud
from schemas.auth_schema import AuthContext
from use_cases.audit.record import record
from use_cases.users.protect_last_superadmin import protect_last_superadmin


def delete_user(db: Session, actor: AuthContext, user_id: UUID) -> None:
    if not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat menghapus user.")
    user = users_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User tidak ditemukan.")
    protect_last_superadmin(db, user, user.role, False)
    users_crud.update(db, user, {"is_active": False, "credential_version": user.credential_version + 1})
    auth_sessions_crud.revoke_user_sessions(db, user.id)
    record(db, actor, "disable", "user", user.id)
    db.commit()
