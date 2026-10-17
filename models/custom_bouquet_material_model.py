from decimal import Decimal
from uuid import UUID
from sqlalchemy import CheckConstraint,ForeignKey,Numeric,String,UniqueConstraint,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from configs.model_columns import IdentityMixin
from models.base import Base

class CustomBouquetMaterial(IdentityMixin,Base):
    __tablename__="custom_bouquet_materials"
    __table_args__=(UniqueConstraint("custom_bouquet_id","material_id",name="uq_custom_bouquet_material"),CheckConstraint("quantity_required > 0 AND quantity_required <= 999999999999.999999",name="ck_custom_bouquet_material_quantity"),)
    custom_bouquet_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("custom_bouquets.id",ondelete="CASCADE"),nullable=False,index=True)
    material_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("materials.id",ondelete="RESTRICT"),nullable=False)
    quantity_required: Mapped[Decimal]=mapped_column(Numeric(20,6),nullable=False)
    unit: Mapped[str]=mapped_column(String(32),nullable=False)
