from sqlalchemy.orm import Session

from models.user_model import User
from schemas.auth_schema import AuthContext
from schemas.user_schema import ProfileUpdate, UserUpdate
from use_cases.users.update_user import update_user


def update_profile(db: Session, actor: AuthContext, data: ProfileUpdate) -> User:
    return update_user(db, actor, actor.user.id, UserUpdate(**data.model_dump(exclude_unset=True)), "unknown")
