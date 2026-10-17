from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("status IN ('draft','confirmed','in_production','ready','completed','cancelled')", name="ck_orders_status"),
        CheckConstraint("payment_status IN ('unpaid','partial','paid')", name="ck_orders_payment_status"),
        CheckConstraint("fulfillment_method IN ('pickup','delivery')", name="ck_orders_fulfillment"),
        CheckConstraint("length(trim(customer_name)) > 0", name="ck_orders_customer"),
        CheckConstraint("fulfillment_method <> 'delivery' OR (customer_address IS NOT NULL AND length(trim(customer_address)) > 0)", name="ck_orders_delivery_address"),
        CheckConstraint("subtotal >= 0 AND subtotal <= 999999999999999 AND discount_amount >= 0 AND shipping_charge >= 0 AND total_amount >= 0 AND total_amount <= 999999999999999", name="ck_orders_amounts"),
        CheckConstraint("total_amount = subtotal + shipping_charge - discount_amount", name="ck_orders_total_matches"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    order_number: Mapped[str] = mapped_column(String(48), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    customer_phone: Mapped[str | None] = mapped_column(String(50))
    customer_address: Mapped[str | None] = mapped_column(Text)
    customer_notes: Mapped[str | None] = mapped_column(Text)
    sales_channel: Mapped[str] = mapped_column(String(32), nullable=False, default="other", index=True)
    fulfillment_method: Mapped[str] = mapped_column(String(16), nullable=False, default="pickup")
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    required_date: Mapped[date | None] = mapped_column(Date, index=True)
    subtotal: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    discount_amount: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    shipping_charge: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_amount: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft", index=True)
    payment_status: Mapped[str] = mapped_column(String(16), nullable=False, default="unpaid", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    production_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
