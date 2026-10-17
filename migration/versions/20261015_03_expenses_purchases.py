"""Raw-material purchase expenses with historical supplier snapshots.

Revision ID: 20261015_03
Revises: 20261014_02
"""

from alembic import op
import sqlalchemy as sa

revision = "20261015_03"
down_revision = "20261014_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=True),
        sa.Column("material_name", sa.String(150), nullable=False),
        sa.Column("store_name", sa.String(150), nullable=False),
        sa.Column("purchase_url", sa.String(2048), nullable=False),
        sa.Column("pack_quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("variant", sa.String(150), nullable=True),
        sa.Column("marketplace", sa.String(50), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("pack_count", sa.Integer(), nullable=False),
        sa.Column("price_per_pack", sa.Numeric(14, 2), nullable=False),
        sa.Column("shipping_cost", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("discount_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("reference_number", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("pack_count >= 1 AND pack_count <= 1000000", name="ck_expenses_pack_count"),
        sa.CheckConstraint("pack_quantity > 0 AND pack_quantity <= 999999999.999", name="ck_expenses_pack_quantity"),
        sa.CheckConstraint("price_per_pack >= 0 AND price_per_pack <= 999999999999.99", name="ck_expenses_price"),
        sa.CheckConstraint("shipping_cost >= 0 AND shipping_cost <= 999999999999.99", name="ck_expenses_shipping"),
        sa.CheckConstraint("discount_amount >= 0 AND discount_amount <= 999999999999.99", name="ck_expenses_discount"),
        sa.CheckConstraint("subtotal_amount >= 0 AND subtotal_amount <= 999999999999999999.99", name="ck_expenses_subtotal"),
        sa.CheckConstraint("total_amount >= 0 AND total_amount <= 999999999999999999.99", name="ck_expenses_total"),
        sa.CheckConstraint("subtotal_amount = round(price_per_pack * pack_count, 2)", name="ck_expenses_subtotal_matches"),
        sa.CheckConstraint("total_amount = round(subtotal_amount + shipping_cost - discount_amount, 2)", name="ck_expenses_total_matches"),
        sa.CheckConstraint("length(trim(material_name)) > 0", name="ck_expenses_material_name"),
        sa.CheckConstraint("length(trim(store_name)) > 0", name="ck_expenses_store_name"),
        sa.CheckConstraint("length(trim(unit)) > 0", name="ck_expenses_unit"),
    )
    for column in ("supplier_id", "material_name", "store_name", "purchase_date", "total_amount", "created_by", "created_at"):
        op.create_index(f"ix_expenses_{column}", "expenses", [column])
    op.execute('ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY')
    op.execute('REVOKE ALL ON TABLE public.expenses FROM PUBLIC, anon, authenticated, service_role')


def downgrade() -> None:
    op.drop_table("expenses")
