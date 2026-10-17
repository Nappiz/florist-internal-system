from sqlalchemy.orm import Session

from models.user_model import User
from schemas.auth_schema import AuthContext
from schemas.user_schema import PasswordUpdate, UserUpdate
from use_cases.users.update_user import update_user


def change_password(db: Session, actor: AuthContext, data: PasswordUpdate, client_ip: str) -> User:
    return update_user(db, actor, actor.user.id, UserUpdate(password=data.password, current_password=data.current_password), client_ip)
