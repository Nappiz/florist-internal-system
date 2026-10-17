from uuid import UUID, uuid4
from sqlalchemy import Boolean, CheckConstraint, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class ExpenseCategory(Base):
    __tablename__ = 'expense_categories'
    __table_args__ = (CheckConstraint("classification IN ('operational','equipment','other')", name='ck_expense_category_classification'),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(24), nullable=False, default='operational')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
