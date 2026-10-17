from datetime import UTC,date,datetime
from uuid import UUID
from sqlalchemy import BigInteger,CheckConstraint,Date,DateTime,ForeignKey,String,Text,UniqueConstraint,Uuid
from sqlalchemy.orm import Mapped,mapped_column
from models.base import Base
from configs.model_columns import IdentityMixin


class PurchasePayment(IdentityMixin,Base):
    __tablename__='purchase_payments'
    __table_args__=(CheckConstraint('amount > 0 AND amount <= 999999999999999',name='ck_purchase_payment_amount'),UniqueConstraint('purchase_id','payment_key',name='uq_purchase_payment_key'))
    purchase_id: Mapped[UUID]=mapped_column(Uuid,ForeignKey('purchases.id',ondelete='RESTRICT'),index=True)
    payment_key: Mapped[UUID]=mapped_column(Uuid)
    payment_date: Mapped[date]=mapped_column(Date,index=True)
    amount: Mapped[int]=mapped_column(BigInteger)
    method: Mapped[str | None]=mapped_column(String(50))
    reference_number: Mapped[str | None]=mapped_column(String(100))
    notes: Mapped[str | None]=mapped_column(Text)
    created_by: Mapped[UUID | None]=mapped_column(Uuid,ForeignKey('users.id',ondelete='SET NULL'))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))

    cash_account_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("cash_accounts.id", ondelete="RESTRICT"), index=True)
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
