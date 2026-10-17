from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("pack_count >= 1 AND pack_count <= 1000000", name="ck_expenses_pack_count"),
        CheckConstraint("pack_quantity > 0 AND pack_quantity <= 999999999.999", name="ck_expenses_pack_quantity"),
        CheckConstraint("price_per_pack >= 0 AND price_per_pack <= 999999999999.99", name="ck_expenses_price"),
        CheckConstraint("shipping_cost >= 0 AND shipping_cost <= 999999999999.99", name="ck_expenses_shipping"),
        CheckConstraint("discount_amount >= 0 AND discount_amount <= 999999999999.99", name="ck_expenses_discount"),
        CheckConstraint("subtotal_amount >= 0 AND subtotal_amount <= 999999999999999999.99", name="ck_expenses_subtotal"),
        CheckConstraint("total_amount >= 0 AND total_amount <= 999999999999999999.99", name="ck_expenses_total"),
        CheckConstraint("subtotal_amount = round(price_per_pack * pack_count, 2)", name="ck_expenses_subtotal_matches"),
        CheckConstraint("total_amount = round(subtotal_amount + shipping_cost - discount_amount, 2)", name="ck_expenses_total_matches"),
        CheckConstraint("length(trim(material_name)) > 0", name="ck_expenses_material_name"),
        CheckConstraint("length(trim(store_name)) > 0", name="ck_expenses_store_name"),
        CheckConstraint("length(trim(unit)) > 0", name="ck_expenses_unit"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    supplier_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("suppliers.id", ondelete="SET NULL"), index=True)
    material_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    store_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    purchase_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    pack_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80))
    variant: Mapped[str | None] = mapped_column(String(150))
    marketplace: Mapped[str | None] = mapped_column(String(50))
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pack_count: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_pack: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False, index=True)
    payment_method: Mapped[str | None] = mapped_column(String(50))
    reference_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
