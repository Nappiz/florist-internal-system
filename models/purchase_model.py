from datetime import date
from uuid import UUID
from sqlalchemy import BigInteger,CheckConstraint,Date,ForeignKey,String,Text,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin,TimestampMixin,ActorMixin


class Purchase(IdentityMixin,TimestampMixin,ActorMixin,Base):
    __tablename__='purchases'
    __table_args__=(CheckConstraint('subtotal >= 0 AND discount_amount >= 0 AND shipping_cost >= 0 AND total_amount >= 0 AND total_amount = subtotal + shipping_cost - discount_amount',name='ck_purchase_totals'),CheckConstraint("status IN ('draft','ordered','received','cancelled')",name='ck_purchase_status'),CheckConstraint("payment_status IN ('unpaid','partial','paid')",name='ck_purchase_payment_status'))
    purchase_number: Mapped[str]=mapped_column(String(64),unique=True)
    supplier_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('supplier_stores.id',ondelete='RESTRICT'),index=True)
    purchase_date: Mapped[date]=mapped_column(Date,index=True)
    reference_number: Mapped[str | None]=mapped_column(String(100))
    subtotal: Mapped[int]=mapped_column(BigInteger,default=0)
    discount_amount: Mapped[int]=mapped_column(BigInteger,default=0)
    shipping_cost: Mapped[int]=mapped_column(BigInteger,default=0)
    total_amount: Mapped[int]=mapped_column(BigInteger,default=0)
    status: Mapped[str]=mapped_column(String(16),default='draft',index=True)
    payment_status: Mapped[str]=mapped_column(String(16),default='unpaid')
    notes: Mapped[str | None]=mapped_column(Text)
