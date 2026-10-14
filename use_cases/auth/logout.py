from sqlalchemy.orm import Session

from crud import auth_sessions_crud
from schemas.auth_schema import AuthContext


def logout(db: Session, context: AuthContext) -> None:
    auth_sessions_crud.revoke_session(db, context.session.id)
    db.commit()
