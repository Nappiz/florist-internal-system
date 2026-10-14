from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from configs.body_limit_middleware import BodyLimitMiddleware
from configs.settings import get_settings
from routes.auth import router as auth_router
from routes.health import router as health_router
from routes.users import router as users_router


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title="Sistem Florist API")
    application.add_middleware(BodyLimitMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    if settings.app_env == "production":
        application.add_middleware(HTTPSRedirectMiddleware)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, error: RequestValidationError):
        # FastAPI normally echoes rejected input, which may contain a password.
        details = [{key: item[key] for key in ("loc", "msg", "type")} for item in error.errors()]
        return JSONResponse(status_code=422, content={"detail": details})

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if settings.app_env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(users_router)
    return application


app = create_app()
