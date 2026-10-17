from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin, TimestampMixin


class Material(IdentityMixin, TimestampMixin, Base):
    __tablename__ = 'materials'
    __table_args__ = (CheckConstraint('minimum_stock >= 0 AND minimum_stock <= 999999999999.999999', name='ck_material_minimum'), CheckConstraint('length(trim(name)) > 0', name='ck_material_name'))
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    base_unit: Mapped[str] = mapped_column(String(32), default='pcs')
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(20,6), default=Decimal('0'))
    image_url: Mapped[str | None] = mapped_column(String(2048))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
