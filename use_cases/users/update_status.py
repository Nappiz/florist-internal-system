from sqlalchemy.orm import Session
from uuid import UUID

from models.user_model import User
from schemas.auth_schema import AuthContext
from schemas.user_schema import StatusInput, UserUpdate
from use_cases.users.update_user import update_user


def update_status(db: Session, actor: AuthContext, user_id: UUID, data: StatusInput) -> User:
    return update_user(db, actor, user_id, UserUpdate(is_active=data.is_active), "unknown")
