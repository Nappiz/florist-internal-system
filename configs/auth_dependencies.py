from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from configs.database import get_db
from configs.settings import get_settings
from schemas.auth_schema import AuthContext
from use_cases.auth.authenticate_session import authenticate_session
from use_cases.auth.validate_origin import validate_origin
from use_cases.auth.verify_csrf import verify_csrf


def authenticated_context(request: Request, db: Session = Depends(get_db)) -> AuthContext:
    return authenticate_session(db, request.cookies.get(get_settings().session_cookie_name))


def csrf_context(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    context: AuthContext = Depends(authenticated_context),
) -> AuthContext:
    return verify_csrf(context, csrf_token, request.headers.get("Origin"))


def trusted_origin(request: Request) -> None:
    validate_origin(request.headers.get("Origin"))
