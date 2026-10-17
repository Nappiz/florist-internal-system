from decimal import Decimal
from uuid import UUID
from sqlalchemy import BigInteger,CheckConstraint,ForeignKey,Integer,Numeric,UniqueConstraint,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin

class CustomBouquetFlower(IdentityMixin,Base):
    __tablename__="custom_bouquet_flowers"
    __table_args__=(UniqueConstraint("custom_bouquet_id","flower_id",name="uq_custom_bouquet_flower"),CheckConstraint("estimated_hpp_snapshot IS NULL OR (estimated_hpp_snapshot >= 0 AND estimated_hpp_snapshot < 1000000000000000000000000000000)",name="ck_custom_bouquet_flower_hpp"),CheckConstraint("quantity BETWEEN 1 AND 1000000 AND unit_price_snapshot BETWEEN 0 AND 999999999999999",name="ck_custom_bouquet_flower_bounds"),)
    custom_bouquet_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("custom_bouquets.id",ondelete="CASCADE"),nullable=False,index=True)
    flower_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("flowers.id",ondelete="RESTRICT"),nullable=False)
    quantity: Mapped[int]=mapped_column(Integer,nullable=False)
    estimated_hpp_snapshot: Mapped[Decimal|None]=mapped_column(Numeric(38,8))
    unit_price_snapshot: Mapped[int]=mapped_column(BigInteger,nullable=False)
