from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context
from configs.database import get_db
from schemas.report_schema import InventoryReport, ProfitabilityReport, PurchaseReport, ReportQuery, SalesReport
from use_cases.reports.inventory import inventory_report
from use_cases.reports.profitability import profitability_report
from use_cases.reports.purchases import purchases_report
from use_cases.reports.sales import sales_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/purchases", response_model=PurchaseReport)
def purchases_endpoint(query: Annotated[ReportQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return purchases_report(db, actor, query)


@router.get("/sales", response_model=SalesReport)
def sales_endpoint(query: Annotated[ReportQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return sales_report(db, actor, query)


@router.get("/inventory", response_model=InventoryReport)
def inventory_endpoint(query: Annotated[ReportQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return inventory_report(db, actor, query)


@router.get("/profitability", response_model=ProfitabilityReport)
def profitability_endpoint(query: Annotated[ReportQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return profitability_report(db, actor, query)
