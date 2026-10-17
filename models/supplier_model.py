from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        CheckConstraint("price >= 0 AND price <= 999999999999.99", name="ck_suppliers_price_range"),
        CheckConstraint("pack_quantity > 0 AND pack_quantity <= 999999999.999", name="ck_suppliers_quantity_range"),
        CheckConstraint("estimated_shipping_cost IS NULL OR (estimated_shipping_cost >= 0 AND estimated_shipping_cost <= 999999999999.99)", name="ck_suppliers_shipping_range"),
        CheckConstraint("length(trim(material_name)) > 0", name="ck_suppliers_material_name"),
        CheckConstraint("length(trim(store_name)) > 0", name="ck_suppliers_store_name"),
        CheckConstraint("length(trim(unit)) > 0", name="ck_suppliers_unit"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    material_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    store_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    purchase_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    pack_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("1"))
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="pcs")
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    variant: Mapped[str | None] = mapped_column(String(150))
    marketplace: Mapped[str | None] = mapped_column(String(50))
    estimated_shipping_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    last_checked_at: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
