from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.report_schema import Period, ReportQuery


class AuditQuery(ReportQuery):
    actor_id: UUID | None = None
    action: str | None = Field(None, min_length=1, max_length=64)
    entity_type: str | None = Field(None, min_length=1, max_length=64)
    entity_id: UUID | None = None
    limit: int = Field(50, ge=1, le=100)


class AuditEntry(BaseModel):
    id: UUID
    actor_id: UUID | None
    action: str
    entity_type: str
    entity_id: UUID | None
    details: dict | None
    created_at: datetime


class AuditPage(BaseModel):
    period: Period
    items: list[AuditEntry]
    total: int
    limit: int
    offset: int
