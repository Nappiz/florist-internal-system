from datetime import UTC,datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import CheckConstraint,DateTime,ForeignKey,Numeric,String,Text,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin


class InventoryMovement(IdentityMixin,Base):
    __tablename__='inventory_movements'
    __table_args__=(CheckConstraint('quantity_delta != 0 AND quantity_delta >= -999999999999.999999 AND quantity_delta <= 999999999999.999999 AND unit_cost_snapshot >= 0 AND unit_cost_snapshot <= 9999999999999999.99999999',name='ck_movement_values'),CheckConstraint("movement_type IN ('IN','OUT','ADJUSTMENT')",name='ck_movement_type'))
    event_key: Mapped[str]=mapped_column(String(160),unique=True)
    material_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('materials.id',ondelete='RESTRICT'),index=True)
    movement_type: Mapped[str]=mapped_column(String(16))
    quantity_delta: Mapped[Decimal]=mapped_column(Numeric(20,6))
    unit_cost_snapshot: Mapped[Decimal]=mapped_column(Numeric(24,8))
    reference_type: Mapped[str]=mapped_column(String(32),index=True)
    reference_id: Mapped[UUID]=mapped_column(Uuid,index=True)
    notes: Mapped[str | None]=mapped_column(Text)
    created_by: Mapped[UUID | None]=mapped_column(Uuid,ForeignKey('users.id',ondelete='SET NULL'))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC),index=True)
