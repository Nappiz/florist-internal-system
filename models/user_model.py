from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(username) BETWEEN 3 AND 32", name="ck_users_username_length"),
        CheckConstraint("username = lower(username)", name="ck_users_username_lowercase"),
        CheckConstraint("role IN ('staff', 'superadmin')", name="ck_users_role"),
        CheckConstraint("is_superadmin = (role = 'superadmin')", name="ck_users_role_compatibility"),
        Index("uq_users_email_lower", text("lower(email)"), unique=True),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False, default=lambda context: context.get_current_parameters()["username"])
    email: Mapped[str] = mapped_column(String(254), nullable=False, default=lambda context: context.get_current_parameters()["username"] + "@legacy.invalid")
    role: Mapped[str] = mapped_column(String(16), nullable=False, default=lambda context: "superadmin" if context.get_current_parameters().get("is_superadmin") else "staff")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    credential_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
