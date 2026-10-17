from datetime import UTC, date, datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class ExpensePayment(Base):
    __tablename__ = 'expense_payments'
    __table_args__ = (CheckConstraint('amount > 0 AND amount <= 999999999999999', name='ck_expense_payment_amount'),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    expense_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('operating_expenses.id'), nullable=False, index=True)
    payment_key: Mapped[UUID] = mapped_column(Uuid, nullable=False, unique=True)
    cash_account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('cash_accounts.id'), nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    proof_url: Mapped[str | None] = mapped_column(String(2048))
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
