from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base


class InventoryBalance(Base):
    __tablename__='inventory_balances'
    __table_args__=(CheckConstraint('quantity_on_hand >= 0 AND quantity_on_hand <= 999999999999.999999 AND average_unit_cost >= 0 AND average_unit_cost <= 9999999999999999.99999999',name='ck_inventory_nonnegative'),)
    material_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('materials.id',ondelete='RESTRICT'),primary_key=True)
    quantity_on_hand: Mapped[Decimal]=mapped_column(Numeric(20,6),default=Decimal('0'))
    average_unit_cost: Mapped[Decimal]=mapped_column(Numeric(24,8),default=Decimal('0'))
    has_received_cost: Mapped[bool]=mapped_column(Boolean,default=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),onupdate=lambda:datetime.now(UTC))
