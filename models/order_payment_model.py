from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class OrderPayment(Base):
    __tablename__ = "order_payments"
    __table_args__ = (
        UniqueConstraint("order_id", "payment_key", name="uq_order_payment_key"),
        CheckConstraint("amount > 0 AND amount <= 999999999999999", name="ck_order_payments_amount"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_key: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str | None] = mapped_column(String(50))
    reference_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    cash_account_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("cash_accounts.id", ondelete="RESTRICT"), index=True)
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
