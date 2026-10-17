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
from routes.users import versioned_router as users_v1_router
from routes.suppliers import router as suppliers_router
from routes.expenses import router as expenses_router
from routes.materials import router as materials_router
from routes.supplier_stores import router as supplier_stores_router
from routes.supplier_materials import router as supplier_materials_router
from routes.inventory import router as inventory_router
from routes.purchases import router as purchases_router
from routes.flowers import router as flowers_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.dashboard import router as dashboard_router
from routes.reports import router as reports_router
from routes.audit import router as audit_router
from routes.legacy import router as legacy_router
from routes.operational_expenses import router as operational_expenses_router
from routes.expense_categories import router as expense_categories_router
from routes.custom_bouquets import router as custom_bouquets_router
from routes.bouquet_options import router as bouquet_options_router
from routes.bouquet_settings import router as bouquet_settings_router
from routes.cash_accounts import router as cash_accounts_router
from routes.cashflow import router as cashflow_router


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title="Sistem Florist API")
    application.add_middleware(BodyLimitMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
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
    application.include_router(legacy_router)
    for router in (auth_router,users_v1_router,materials_router,supplier_stores_router,supplier_materials_router,inventory_router,purchases_router,flowers_router,products_router,orders_router,dashboard_router,reports_router,audit_router):
        application.include_router(router,prefix='/api/v1')
    for router in (operational_expenses_router, expense_categories_router, custom_bouquets_router, bouquet_options_router, bouquet_settings_router, cash_accounts_router, cashflow_router):
        application.include_router(router, prefix="/api/v1")
    return application


app = create_app()
