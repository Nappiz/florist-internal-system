from decimal import Decimal
from uuid import UUID
from sqlalchemy import BigInteger,CheckConstraint,ForeignKey,Numeric,String,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin


class PurchaseItem(IdentityMixin,Base):
    __tablename__='purchase_items'
    __table_args__=(CheckConstraint('quantity > 0 AND quantity_base > 0 AND unit_price >= 0 AND subtotal >= 0',name='ck_purchase_item_values'),)
    purchase_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('purchases.id',ondelete='RESTRICT'),index=True)
    material_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('materials.id',ondelete='RESTRICT'),index=True)
    supplier_listing_id: Mapped[UUID | None]=mapped_column(Uuid,ForeignKey('supplier_materials.id',ondelete='RESTRICT'))
    material_name_snapshot: Mapped[str]=mapped_column(String(150))
    base_unit_snapshot: Mapped[str]=mapped_column(String(32))
    quantity: Mapped[Decimal]=mapped_column(Numeric(20,6))
    quantity_base: Mapped[Decimal]=mapped_column(Numeric(20,6))
    unit_price: Mapped[int]=mapped_column(BigInteger)
    subtotal: Mapped[int]=mapped_column(BigInteger)
