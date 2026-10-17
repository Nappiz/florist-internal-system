"""Bound Decimal columns explicitly, including PostgreSQL nonfinite values.

Revision ID: 20261015_05
Revises: a11c6331bb7c
"""
from alembic import op

revision='20261015_05'
down_revision='a11c6331bb7c'
branch_labels=None
depends_on=None


def upgrade():
    for table,name,expression in (
        ('inventory_balances','ck_inventory_nonnegative','quantity_on_hand >= 0 AND quantity_on_hand <= 999999999999.999999 AND average_unit_cost >= 0 AND average_unit_cost <= 9999999999999999.99999999'),
        ('inventory_movements','ck_movement_values','quantity_delta != 0 AND quantity_delta >= -999999999999.999999 AND quantity_delta <= 999999999999.999999 AND unit_cost_snapshot >= 0 AND unit_cost_snapshot <= 9999999999999999.99999999'),
        ('supplier_materials','ck_listing_quantity','package_quantity > 0 AND package_quantity <= 999999999999.999999 AND quantity_in_base_unit > 0 AND quantity_in_base_unit <= 999999999999.999999'),
    ):
        op.drop_constraint(name,table,type_='check')
        op.create_check_constraint(name,table,expression)


def downgrade():
    for table,name,expression in (
        ('inventory_balances','ck_inventory_nonnegative','quantity_on_hand >= 0 AND average_unit_cost >= 0'),
        ('inventory_movements','ck_movement_values','quantity_delta != 0 AND unit_cost_snapshot >= 0'),
        ('supplier_materials','ck_listing_quantity','package_quantity > 0 AND quantity_in_base_unit > 0'),
    ):
        op.drop_constraint(name,table,type_='check')
        op.create_check_constraint(name,table,expression)
