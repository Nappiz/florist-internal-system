from datetime import UTC, date, datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class CashTransaction(Base):
    __tablename__ = 'cash_transactions'
    __table_args__ = (
        UniqueConstraint('source_type', 'source_id', name='uq_cash_source'),
        CheckConstraint("direction IN ('IN','OUT')", name='ck_cash_direction'),
        CheckConstraint('amount > 0 AND amount <= 999999999999999', name='ck_cash_amount'),
        Index('ix_cash_account_chronology', 'cash_account_id', 'transaction_date', 'created_at', 'id'),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    transaction_number: Mapped[str] = mapped_column(String(48), nullable=False, unique=True)
    cash_account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('cash_accounts.id', ondelete='RESTRICT'), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    operation_key: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('cash_operations.operation_key', ondelete='RESTRICT'), index=True)
    reversal_of_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('cash_transactions.id', ondelete='RESTRICT'), unique=True)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
