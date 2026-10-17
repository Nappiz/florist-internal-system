from datetime import UTC, datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class IdentityMixin:
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class ActorMixin:
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
    updated_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
