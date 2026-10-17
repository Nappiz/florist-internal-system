from decimal import Decimal
from sqlalchemy import BigInteger,Boolean,CheckConstraint,Integer,JSON,Numeric,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from configs.model_columns import IdentityMixin,TimestampMixin,ActorMixin
from models.base import Base

class CustomBouquet(IdentityMixin,TimestampMixin,ActorMixin,Base):
    __tablename__="custom_bouquets"
    __table_args__=(CheckConstraint("status IN ('draft','finalized','archived')",name="ck_custom_bouquet_status"),CheckConstraint("proposed_price BETWEEN 0 AND 999999999999999 AND (final_price IS NULL OR final_price BETWEEN 0 AND 999999999999999) AND assembly_fee BETWEEN 0 AND 999999999999999 AND assembly_labor_cost >= 0 AND assembly_labor_cost < 1000000000000000000000000000000 AND (estimated_hpp IS NULL OR (estimated_hpp >= 0 AND estimated_hpp < 1000000000000000000000000000000))",name="ck_custom_bouquet_amounts"),)
    configuration_number: Mapped[str]=mapped_column(String(40),nullable=False,unique=True)
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    status: Mapped[str]=mapped_column(String(16),nullable=False,default="draft")
    customer_reference: Mapped[str|None]=mapped_column(String(150))
    description: Mapped[str|None]=mapped_column(Text)
    image_reference: Mapped[str|None]=mapped_column(String(2048))
    personalization: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    estimated_hpp: Mapped[Decimal|None]=mapped_column(Numeric(38,8))
    cost_complete: Mapped[bool]=mapped_column(Boolean,nullable=False,default=False)
    proposed_price: Mapped[int]=mapped_column(BigInteger,nullable=False)
    final_price: Mapped[int|None]=mapped_column(BigInteger)
    price_override_reason: Mapped[str|None]=mapped_column(Text)
    assembly_fee: Mapped[int]=mapped_column(BigInteger,nullable=False,default=0)
    assembly_labor_cost: Mapped[Decimal]=mapped_column(Numeric(38,8),nullable=False,default=Decimal(0))
    pricing_version: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    recipe_snapshot: Mapped[dict]=mapped_column(JSON,nullable=False)
