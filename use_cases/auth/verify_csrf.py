import hmac
import re

from fastapi import HTTPException

from schemas.auth_schema import AuthContext
from use_cases.auth.validate_origin import validate_origin


def verify_csrf(context: AuthContext, supplied_token: str | None, origin: str | None) -> AuthContext:
    validate_origin(origin)
    if supplied_token is None or re.fullmatch(r"[a-f0-9]{64}", supplied_token) is None or not hmac.compare_digest(context.csrf_token, supplied_token):
        raise HTTPException(403, "CSRF token tidak valid.")
    return context
