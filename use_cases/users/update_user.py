from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, users_crud
from models.user_model import User
from schemas.auth_schema import AuthContext
from schemas.user_schema import UserUpdate
from services.user_security import hash_password, verify_password
from use_cases.auth.reserve_auth_attempt import reserve_auth_attempt
from use_cases.users.validate_password import validate_password
from use_cases.audit.record import record
from use_cases.users.protect_last_superadmin import protect_last_superadmin


def update_user(db: Session, actor: AuthContext, user_id: UUID, data: UserUpdate, client_ip: str) -> User:
    if not actor.user.is_superadmin and actor.user.id != user_id:
        raise HTTPException(403, "Tidak diizinkan mengubah user lain.")
    if not actor.user.is_superadmin and data.model_fields_set & {"role", "is_active"}:
        raise HTTPException(403, "Hanya superadmin dapat mengubah role atau status user.")
    user = users_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User tidak ditemukan.")
    if user.is_superadmin and not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat mengubah akun superadmin.")
    mutation_fields = data.model_fields_set - {"current_password"}
    if not mutation_fields or any(getattr(data, field) is None for field in mutation_fields):
        raise HTTPException(422, "Isi perubahan user; nilai tidak boleh null.")
    if actor.user.id == user.id and mutation_fields & {"username", "password"}:
        reserve_auth_attempt(db, user.username, client_ip)
        if data.current_password is None or not verify_password(user.password_hash, data.current_password.get_secret_value()):
            db.commit()
            raise HTTPException(403, "Current password tidak valid.")
    values = {}
    for field in mutation_fields & {"full_name", "email", "role", "is_active"}:
        values[field] = getattr(data, field)
    if "role" in values:
        values["is_superadmin"] = values["role"] == "superadmin"
    protect_last_superadmin(db, user, values.get("role", user.role), values.get("is_active", user.is_active))
    if data.username is not None:
        username = data.username.lower()
        if username == "superadmin" and not user.is_superadmin:
            raise HTTPException(409, "Username tidak tersedia.")
        values["username"] = username
    if data.password is not None:
        password = data.password.get_secret_value()
        validate_password(password)
        values["password_hash"] = hash_password(password)
    revoke_sessions = bool(mutation_fields & {"username", "password"}) or values.get("is_active") is False
    if revoke_sessions:
        values["credential_version"] = user.credential_version + 1
    try:
        users_crud.update(db, user, values)
        if revoke_sessions:
            auth_sessions_crud.revoke_user_sessions(db, user.id)
        record(db, actor, "update", "user", user.id, {"fields": sorted(mutation_fields)})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username atau email tidak tersedia.") from None
    db.refresh(user)
    return user
