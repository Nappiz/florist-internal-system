from datetime import UTC, date, datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class OperatingExpense(Base):
    __tablename__ = 'operating_expenses'
    __table_args__ = (
        CheckConstraint('amount > 0 AND amount <= 999999999999999', name='ck_operating_expense_amount'),
        CheckConstraint("status IN ('draft','posted','void')", name='ck_operating_expense_status'),
        CheckConstraint("payment_status IN ('unpaid','partial','paid')", name='ck_operating_expense_payment_status'),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    expense_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    category_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('expense_categories.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    vendor_name: Mapped[str | None] = mapped_column(String(150))
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='draft', index=True)
    payment_status: Mapped[str] = mapped_column(String(16), nullable=False, default='unpaid', index=True)
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=False, index=True)
    posted_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id'))
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    voided_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey('users.id'))
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    void_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
