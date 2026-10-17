from datetime import UTC,datetime
from uuid import UUID
from sqlalchemy import DateTime,ForeignKey,JSON,String,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin


class AuditLog(IdentityMixin,Base):
    __tablename__='audit_logs'
    actor_id: Mapped[UUID | None]=mapped_column(Uuid,ForeignKey('users.id',ondelete='SET NULL'),index=True)
    action: Mapped[str]=mapped_column(String(64),index=True)
    entity_type: Mapped[str]=mapped_column(String(64),index=True)
    entity_id: Mapped[UUID | None]=mapped_column(Uuid,index=True)
    details: Mapped[dict | None]=mapped_column(JSON)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),index=True)
