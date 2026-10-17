from sqlalchemy import BigInteger, CheckConstraint, Integer, Numeric
from sqlalchemy.orm import Mapped,mapped_column
from decimal import Decimal
from models.base import Base

class BouquetSetting(Base):
    __tablename__="bouquet_settings"
    __table_args__=(CheckConstraint("id = 1 AND min_stems >= 1 AND max_stems >= min_stems AND max_stems <= 1000000 AND minimum_price BETWEEN 0 AND 999999999999999 AND assembly_fee BETWEEN 0 AND 999999999999999 AND assembly_labor_cost >= 0 AND assembly_labor_cost < 1000000000000000000000000000000 AND pricing_version >= 1",name="ck_bouquet_settings_bounds"),)
    id: Mapped[int]=mapped_column(Integer,primary_key=True,default=1)
    min_stems: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    max_stems: Mapped[int]=mapped_column(Integer,nullable=False,default=1000)
    minimum_price: Mapped[int]=mapped_column(BigInteger,nullable=False,default=0)
    assembly_fee: Mapped[int]=mapped_column(BigInteger,nullable=False,default=0)
    assembly_labor_cost: Mapped[Decimal]=mapped_column(Numeric(38,8),nullable=False,default=Decimal(0))
    pricing_version: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
