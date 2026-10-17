from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, JSON, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("(flower_id IS NOT NULL AND product_id IS NULL AND custom_bouquet_id IS NULL) OR (flower_id IS NULL AND product_id IS NOT NULL AND custom_bouquet_id IS NULL) OR (flower_id IS NULL AND product_id IS NULL AND custom_bouquet_id IS NOT NULL)", name="ck_order_items_reference"),
        CheckConstraint("(custom_bouquet_id IS NOT NULL AND item_type = 'CUSTOM_BOUQUET') OR (product_id IS NOT NULL AND item_type = 'PRODUCT') OR (flower_id IS NOT NULL AND item_type = 'FLOWER')", name="ck_order_items_type"),
        CheckConstraint("quantity >= 1 AND quantity <= 1000000", name="ck_order_items_quantity"),
        CheckConstraint("unit_price >= 0 AND unit_price <= 999999999999999 AND subtotal >= 0 AND subtotal <= 999999999999999", name="ck_order_items_amounts"),
        CheckConstraint("subtotal = quantity * unit_price", name="ck_order_items_subtotal"),
        CheckConstraint("labor_cost_snapshot >= 0 AND labor_cost_snapshot <= 999999999999999999999999999999.99999999", name="ck_order_items_labor"),
        CheckConstraint("estimated_hpp_snapshot IS NULL OR (estimated_hpp_snapshot >= 0 AND estimated_hpp_snapshot <= 999999999999999999999999999999.99999999)", name="ck_order_items_hpp"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    flower_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("flowers.id", ondelete="RESTRICT"))
    product_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("products.id", ondelete="RESTRICT"))
    custom_bouquet_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("custom_bouquets.id", ondelete="RESTRICT"))
    item_type: Mapped[str] = mapped_column(String(32), nullable=False, default="FLOWER")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    item_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    subtotal: Mapped[int] = mapped_column(BigInteger, nullable=False)
    recipe_snapshot: Mapped[dict | None] = mapped_column(JSON)
    labor_cost_snapshot: Mapped[Decimal] = mapped_column(Numeric(38, 8), nullable=False, default=Decimal("0"))
    estimated_hpp_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(38, 8))
    cost_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
