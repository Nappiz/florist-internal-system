from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context
from configs.database import get_db
from schemas.audit_schema import AuditPage, AuditQuery
from use_cases.audit.list import list_audit

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditPage)
def audit_endpoint(query: Annotated[AuditQuery, Query()], actor=Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_audit(db, actor, query)
