from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Flower(Base):
    __tablename__ = "flowers"
    __table_args__ = (
        CheckConstraint("selling_price >= 0", name="ck_flowers_price_nonnegative"),
        CheckConstraint("estimated_labor_cost >= 0", name="ck_flowers_labor_nonnegative"),
        CheckConstraint("length(trim(sku)) > 0 AND length(trim(name)) > 0", name="ck_flowers_names"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(2048))
    selling_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    estimated_labor_cost: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

