from uuid import UUID
from sqlalchemy import BigInteger,CheckConstraint,ForeignKey,Integer,UniqueConstraint,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin

class CustomBouquetOption(IdentityMixin,Base):
    __tablename__="custom_bouquet_options"
    __table_args__=(UniqueConstraint("custom_bouquet_id","bouquet_option_id",name="uq_custom_bouquet_option"),CheckConstraint("quantity BETWEEN 1 AND 1000000 AND selling_price_snapshot BETWEEN 0 AND 999999999999999",name="ck_custom_bouquet_option_bounds"),)
    custom_bouquet_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("custom_bouquets.id",ondelete="CASCADE"),nullable=False,index=True)
    bouquet_option_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey("bouquet_options.id",ondelete="RESTRICT"),nullable=False)
    quantity: Mapped[int]=mapped_column(Integer,nullable=False)
    selling_price_snapshot: Mapped[int]=mapped_column(BigInteger,nullable=False)
