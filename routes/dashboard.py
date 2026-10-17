from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context
from configs.database import get_db
from schemas.report_schema import DashboardQuery, DashboardReport,RecentRecords
from use_cases.dashboard.get import dashboard
from use_cases.dashboard.recent_orders import recent_orders
from use_cases.dashboard.recent_purchases import recent_purchases

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardReport)
@router.get('/summary',response_model=DashboardReport)
def dashboard_endpoint(query: Annotated[DashboardQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return dashboard(db, actor, query)


@router.get('/recent-orders',response_model=RecentRecords)
def recent_orders_endpoint(query:Annotated[DashboardQuery,Query()],actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return recent_orders(db,actor,query)


@router.get('/recent-purchases',response_model=RecentRecords)
def recent_purchases_endpoint(query:Annotated[DashboardQuery,Query()],actor=Depends(authenticated_context),db:Session=Depends(get_db)):
    return recent_purchases(db,actor,query)
