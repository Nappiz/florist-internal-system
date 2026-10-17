from sqlalchemy import BigInteger,Boolean,CheckConstraint,Integer,String,Text
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin,TimestampMixin

class BouquetOption(IdentityMixin,TimestampMixin,Base):
    __tablename__="bouquet_options"
    __table_args__=(CheckConstraint("selling_price BETWEEN 0 AND 999999999999999 AND min_quantity >= 1 AND max_quantity >= min_quantity AND max_quantity <= 1000000",name="ck_bouquet_option_bounds"),CheckConstraint("option_group IN ('wrapping','ribbon','greeting_card','accessory')",name="ck_bouquet_option_group"),)
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    option_group: Mapped[str]=mapped_column(String(32),nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    image_url: Mapped[str|None]=mapped_column(String(2048))
    selling_price: Mapped[int]=mapped_column(BigInteger,nullable=False)
    min_quantity: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    max_quantity: Mapped[int]=mapped_column(Integer,nullable=False,default=100)
    requires_materials: Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    is_active: Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
