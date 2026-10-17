"""Raw-material supplier research.

Revision ID: 20261014_02
Revises: 20261014_01
"""

from alembic import op
import sqlalchemy as sa

revision = "20261014_02"
down_revision = "20261014_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("material_name", sa.String(150), nullable=False),
        sa.Column("store_name", sa.String(150), nullable=False),
        sa.Column("purchase_url", sa.String(2048), nullable=False),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("pack_quantity", sa.Numeric(12, 3), server_default="1", nullable=False),
        sa.Column("unit", sa.String(32), server_default="pcs", nullable=False),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("variant", sa.String(150), nullable=True),
        sa.Column("marketplace", sa.String(50), nullable=True),
        sa.Column("estimated_shipping_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("last_checked_at", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("price >= 0 AND price <= 999999999999.99", name="ck_suppliers_price_range"),
        sa.CheckConstraint("pack_quantity > 0 AND pack_quantity <= 999999999.999", name="ck_suppliers_quantity_range"),
        sa.CheckConstraint("estimated_shipping_cost IS NULL OR (estimated_shipping_cost >= 0 AND estimated_shipping_cost <= 999999999999.99)", name="ck_suppliers_shipping_range"),
        sa.CheckConstraint("length(trim(material_name)) > 0", name="ck_suppliers_material_name"),
        sa.CheckConstraint("length(trim(store_name)) > 0", name="ck_suppliers_store_name"),
        sa.CheckConstraint("length(trim(unit)) > 0", name="ck_suppliers_unit"),
    )
    for column in ("material_name", "store_name", "category", "created_by", "created_at"):
        op.create_index(f"ix_suppliers_{column}", "suppliers", [column])
    op.execute('ALTER TABLE public.suppliers ENABLE ROW LEVEL SECURITY')
    op.execute('REVOKE ALL ON TABLE public.suppliers FROM PUBLIC, anon, authenticated, service_role')


def downgrade() -> None:
    op.drop_table("suppliers")
