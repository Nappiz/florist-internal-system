from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin, TimestampMixin


class SupplierMaterial(IdentityMixin, TimestampMixin, Base):
    __tablename__ = 'supplier_materials'
    __table_args__ = (CheckConstraint('listed_price >= 0 AND listed_price <= 999999999999999',name='ck_listing_price'), CheckConstraint('package_quantity > 0 AND package_quantity <= 999999999999.999999 AND quantity_in_base_unit > 0 AND quantity_in_base_unit <= 999999999999.999999',name='ck_listing_quantity'))
    material_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('materials.id',ondelete='RESTRICT'), index=True)
    supplier_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('supplier_stores.id',ondelete='RESTRICT'), index=True)
    listing_name: Mapped[str] = mapped_column(String(150))
    listing_url: Mapped[str | None] = mapped_column(String(2048))
    package_quantity: Mapped[Decimal] = mapped_column(Numeric(20,6))
    package_unit: Mapped[str] = mapped_column(String(32))
    quantity_in_base_unit: Mapped[Decimal] = mapped_column(Numeric(20,6))
    listed_price: Mapped[int] = mapped_column(BigInteger)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(UTC))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,index=True)
