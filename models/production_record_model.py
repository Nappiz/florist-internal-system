from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ProductionRecord(Base):
    __tablename__ = "production_records"
    __table_args__ = (
        CheckConstraint("actual_material_cost >= 0 AND actual_material_cost <= 999999999999999999999999999999.99999999 AND labor_cost_snapshot >= 0 AND labor_cost_snapshot <= 999999999999999999999999999999.99999999 AND total_production_cost >= 0 AND total_production_cost <= 999999999999999999999999999999.99999999", name="ck_production_costs"),
        CheckConstraint("total_production_cost = actual_material_cost + labor_cost_snapshot", name="ck_production_cost_matches"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, unique=True)
    actual_material_cost: Mapped[Decimal] = mapped_column(Numeric(38, 8), nullable=False)
    labor_cost_snapshot: Mapped[Decimal] = mapped_column(Numeric(38, 8), nullable=False)
    total_production_cost: Mapped[Decimal] = mapped_column(Numeric(38, 8), nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
