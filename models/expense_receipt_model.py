from datetime import UTC, datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class ExpenseReceipt(Base):
    __tablename__ = 'expense_receipts'
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    expense_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('operating_expenses.id', ondelete='CASCADE'), nullable=False, index=True)
    storage_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    original_name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
