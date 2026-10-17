from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class FlowerMaterial(Base):
    __tablename__ = "flower_materials"
    __table_args__ = (
        UniqueConstraint("flower_id", "material_id", name="uq_flower_material_component"),
        CheckConstraint("quantity_required > 0", name="ck_flower_material_quantity"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    flower_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("flowers.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("materials.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_required: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)

