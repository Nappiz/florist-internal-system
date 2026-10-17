from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context, trusted_origin
from configs.database import get_db
from configs.settings import get_settings
from schemas.auth_schema import AuthContext, LoginRequest, SessionResponse
from schemas.user_schema import PasswordUpdate, ProfileUpdate, UserResponse
from use_cases.auth.login import login
from use_cases.auth.logout import logout
from use_cases.users.change_password import change_password
from use_cases.users.update_profile import update_profile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SessionResponse, dependencies=[Depends(trusted_origin)])
def login_endpoint(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    result = login(db, data, request.client.host if request.client else "unknown")
    settings = get_settings()
    response.set_cookie(
        settings.session_cookie_name,
        result.token,
        max_age=86400,
        expires=result.expires_at,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="strict",
        path="/",
    )
    return SessionResponse(
        user=UserResponse.model_validate(result.user),
        csrf_token=result.csrf_token,
        expires_at=result.expires_at,
    )


@router.get("/me", response_model=SessionResponse)
def me_endpoint(context: AuthContext = Depends(authenticated_context)):
    return SessionResponse(
        user=UserResponse.model_validate(context.user),
        csrf_token=context.csrf_token,
        expires_at=context.session.expires_at,
    )


@router.post("/logout", status_code=204)
def logout_endpoint(response: Response, context: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    logout(db, context)
    settings = get_settings()
    response.delete_cookie(
        settings.session_cookie_name,
        path="/",
        httponly=True,
        secure=settings.app_env == "production",
        samesite="strict",
    )


@router.patch("/me/profile", response_model=UserResponse)
def profile_endpoint(data: ProfileUpdate, context: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_profile(db, context, data)


@router.patch("/me/password", response_model=UserResponse)
def password_endpoint(data: PasswordUpdate, request: Request, context: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return change_password(db, context, data, request.client.host if request.client else "unknown")
