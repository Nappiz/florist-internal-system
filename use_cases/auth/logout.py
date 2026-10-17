from sqlalchemy.orm import Session

from crud import auth_sessions_crud
from schemas.auth_schema import AuthContext
from use_cases.audit.record import record


def logout(db: Session, context: AuthContext) -> None:
    auth_sessions_crud.revoke_session(db, context.session.id)
    record(db, context, "logout", "user", context.user.id)
    db.commit()
