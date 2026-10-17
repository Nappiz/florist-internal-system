from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ProductFlower(Base):
    __tablename__ = "product_flowers"
    __table_args__ = (
        UniqueConstraint("product_id", "flower_id", name="uq_product_flower_component"),
        CheckConstraint("quantity_required > 0", name="ck_product_flower_quantity"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    flower_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("flowers.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_required: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)

