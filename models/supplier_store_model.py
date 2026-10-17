from sqlalchemy import Boolean, CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin, TimestampMixin


class SupplierStore(IdentityMixin, TimestampMixin, Base):
    __tablename__ = 'supplier_stores'
    __table_args__ = (CheckConstraint("platform IN ('shopee','tokopedia','tiktok','offline','other')",name='ck_supplier_store_platform'), CheckConstraint('length(trim(name)) > 0',name='ck_supplier_store_name'))
    name: Mapped[str] = mapped_column(String(150), index=True)
    platform: Mapped[str] = mapped_column(String(16), default='other', index=True)
    shop_url: Mapped[str | None] = mapped_column(String(2048))
    contact: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
