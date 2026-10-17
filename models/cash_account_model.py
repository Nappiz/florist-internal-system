from datetime import UTC, date, datetime
from uuid import UUID, uuid4
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class CashAccount(Base):
    __tablename__ = 'cash_accounts'
    __table_args__ = (
        CheckConstraint("account_type IN ('cash','bank','e_wallet')", name='ck_cash_account_type'),
        CheckConstraint("history_mode IN ('opening','backfill')", name='ck_cash_account_history_mode'),
        CheckConstraint('length(trim(name)) > 0', name='ck_cash_account_name'),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    account_type: Mapped[str] = mapped_column(String(16), nullable=False)
    opening_date: Mapped[date] = mapped_column(Date, nullable=False)
    history_mode: Mapped[str] = mapped_column(String(16), nullable=False, default='opening')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
