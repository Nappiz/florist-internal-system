"""prd_catalogue_purchasing_production_inventory

Revision ID: a11c6331bb7c
Revises: 20261015_03
Create Date: 2026-10-15 20:36:49.254599
"""

from typing import Sequence, Union
from datetime import UTC,datetime,time
from decimal import Decimal,ROUND_HALF_UP
from uuid import UUID,uuid5
from zoneinfo import ZoneInfo

from alembic import op
import sqlalchemy as sa


revision: str = 'a11c6331bb7c'
down_revision: Union[str, Sequence[str], None] = '20261015_03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Reviewed additive migration. Legacy research/expense tables stay intact.
    op.create_table('flowers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('sku', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image_url', sa.String(length=2048), nullable=True),
    sa.Column('selling_price', sa.BigInteger(), nullable=False),
    sa.Column('estimated_labor_cost', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('estimated_labor_cost >= 0', name='ck_flowers_labor_nonnegative'),
    sa.CheckConstraint('length(trim(sku)) > 0 AND length(trim(name)) > 0', name='ck_flowers_names'),
    sa.CheckConstraint('selling_price >= 0', name='ck_flowers_price_nonnegative'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_flowers_category'), 'flowers', ['category'], unique=False)
    op.create_index(op.f('ix_flowers_is_active'), 'flowers', ['is_active'], unique=False)
    op.create_index(op.f('ix_flowers_name'), 'flowers', ['name'], unique=False)
    op.create_table('materials',
    sa.Column('sku', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('base_unit', sa.String(length=32), nullable=False),
    sa.Column('minimum_stock', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('image_url', sa.String(length=2048), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('length(trim(name)) > 0', name='ck_material_name'),
    sa.CheckConstraint('minimum_stock >= 0 AND minimum_stock <= 999999999999.999999', name='ck_material_minimum'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_materials_category'), 'materials', ['category'], unique=False)
    op.create_index(op.f('ix_materials_is_active'), 'materials', ['is_active'], unique=False)
    op.create_index(op.f('ix_materials_name'), 'materials', ['name'], unique=False)
    op.create_table('products',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('sku', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image_url', sa.String(length=2048), nullable=True),
    sa.Column('selling_price', sa.BigInteger(), nullable=False),
    sa.Column('assembly_labor_cost', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('assembly_labor_cost >= 0', name='ck_products_labor_nonnegative'),
    sa.CheckConstraint('length(trim(sku)) > 0 AND length(trim(name)) > 0', name='ck_products_names'),
    sa.CheckConstraint('selling_price >= 0', name='ck_products_price_nonnegative'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_table('supplier_stores',
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('platform', sa.String(length=16), nullable=False),
    sa.Column('shop_url', sa.String(length=2048), nullable=True),
    sa.Column('contact', sa.String(length=100), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("platform IN ('shopee','tokopedia','tiktok','offline','other')", name='ck_supplier_store_platform'),
    sa.CheckConstraint('length(trim(name)) > 0', name='ck_supplier_store_name'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supplier_stores_is_active'), 'supplier_stores', ['is_active'], unique=False)
    op.create_index(op.f('ix_supplier_stores_name'), 'supplier_stores', ['name'], unique=False)
    op.create_index(op.f('ix_supplier_stores_platform'), 'supplier_stores', ['platform'], unique=False)
    op.create_table('audit_logs',
    sa.Column('actor_id', sa.Uuid(), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('entity_id', sa.Uuid(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_actor_id'), 'audit_logs', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_table('flower_materials',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('flower_id', sa.Uuid(), nullable=False),
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('quantity_required', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=False),
    sa.CheckConstraint('quantity_required > 0', name='ck_flower_material_quantity'),
    sa.ForeignKeyConstraint(['flower_id'], ['flowers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('flower_id', 'material_id', name='uq_flower_material_component')
    )
    op.create_index(op.f('ix_flower_materials_flower_id'), 'flower_materials', ['flower_id'], unique=False)
    op.create_index(op.f('ix_flower_materials_material_id'), 'flower_materials', ['material_id'], unique=False)
    op.create_table('inventory_balances',
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('quantity_on_hand', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('average_unit_cost', sa.Numeric(precision=24, scale=8), nullable=False),
    sa.Column('has_received_cost', sa.Boolean(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('quantity_on_hand >= 0 AND average_unit_cost >= 0', name='ck_inventory_nonnegative'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('material_id')
    )
    op.create_table('inventory_movements',
    sa.Column('event_key', sa.String(length=160), nullable=False),
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('movement_type', sa.String(length=16), nullable=False),
    sa.Column('quantity_delta', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('unit_cost_snapshot', sa.Numeric(precision=24, scale=8), nullable=False),
    sa.Column('reference_type', sa.String(length=32), nullable=False),
    sa.Column('reference_id', sa.Uuid(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint("movement_type IN ('IN','OUT','ADJUSTMENT')", name='ck_movement_type'),
    sa.CheckConstraint('quantity_delta != 0 AND unit_cost_snapshot >= 0', name='ck_movement_values'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('event_key')
    )
    op.create_index(op.f('ix_inventory_movements_created_at'), 'inventory_movements', ['created_at'], unique=False)
    op.create_index(op.f('ix_inventory_movements_material_id'), 'inventory_movements', ['material_id'], unique=False)
    op.create_index(op.f('ix_inventory_movements_reference_id'), 'inventory_movements', ['reference_id'], unique=False)
    op.create_index(op.f('ix_inventory_movements_reference_type'), 'inventory_movements', ['reference_type'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_number', sa.String(length=48), nullable=False),
    sa.Column('customer_name', sa.String(length=150), nullable=False),
    sa.Column('customer_phone', sa.String(length=50), nullable=True),
    sa.Column('customer_address', sa.Text(), nullable=True),
    sa.Column('customer_notes', sa.Text(), nullable=True),
    sa.Column('sales_channel', sa.String(length=32), nullable=False),
    sa.Column('fulfillment_method', sa.String(length=16), nullable=False),
    sa.Column('order_date', sa.Date(), nullable=False),
    sa.Column('required_date', sa.Date(), nullable=True),
    sa.Column('subtotal', sa.BigInteger(), nullable=False),
    sa.Column('discount_amount', sa.BigInteger(), nullable=False),
    sa.Column('shipping_charge', sa.BigInteger(), nullable=False),
    sa.Column('total_amount', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('payment_status', sa.String(length=16), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('production_started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ready_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("fulfillment_method <> 'delivery' OR (customer_address IS NOT NULL AND length(trim(customer_address)) > 0)", name='ck_orders_delivery_address'),
    sa.CheckConstraint("fulfillment_method IN ('pickup','delivery')", name='ck_orders_fulfillment'),
    sa.CheckConstraint("payment_status IN ('unpaid','partial','paid')", name='ck_orders_payment_status'),
    sa.CheckConstraint("status IN ('draft','confirmed','in_production','ready','completed','cancelled')", name='ck_orders_status'),
    sa.CheckConstraint('length(trim(customer_name)) > 0', name='ck_orders_customer'),
    sa.CheckConstraint('subtotal >= 0 AND subtotal <= 999999999999999 AND discount_amount >= 0 AND shipping_charge >= 0 AND total_amount >= 0 AND total_amount <= 999999999999999', name='ck_orders_amounts'),
    sa.CheckConstraint('total_amount = subtotal + shipping_charge - discount_amount', name='ck_orders_total_matches'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_number')
    )
    op.create_index(op.f('ix_orders_customer_name'), 'orders', ['customer_name'], unique=False)
    op.create_index(op.f('ix_orders_order_date'), 'orders', ['order_date'], unique=False)
    op.create_index(op.f('ix_orders_payment_status'), 'orders', ['payment_status'], unique=False)
    op.create_index(op.f('ix_orders_required_date'), 'orders', ['required_date'], unique=False)
    op.create_index(op.f('ix_orders_sales_channel'), 'orders', ['sales_channel'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    op.create_table('product_flowers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('flower_id', sa.Uuid(), nullable=False),
    sa.Column('quantity_required', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.CheckConstraint('quantity_required > 0', name='ck_product_flower_quantity'),
    sa.ForeignKeyConstraint(['flower_id'], ['flowers.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id', 'flower_id', name='uq_product_flower_component')
    )
    op.create_index(op.f('ix_product_flowers_flower_id'), 'product_flowers', ['flower_id'], unique=False)
    op.create_index(op.f('ix_product_flowers_product_id'), 'product_flowers', ['product_id'], unique=False)
    op.create_table('product_materials',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('quantity_required', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=False),
    sa.CheckConstraint('quantity_required > 0', name='ck_product_material_quantity'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id', 'material_id', name='uq_product_material_component')
    )
    op.create_index(op.f('ix_product_materials_material_id'), 'product_materials', ['material_id'], unique=False)
    op.create_index(op.f('ix_product_materials_product_id'), 'product_materials', ['product_id'], unique=False)
    op.create_table('purchases',
    sa.Column('purchase_number', sa.String(length=64), nullable=False),
    sa.Column('supplier_id', sa.Uuid(), nullable=False),
    sa.Column('purchase_date', sa.Date(), nullable=False),
    sa.Column('reference_number', sa.String(length=100), nullable=True),
    sa.Column('subtotal', sa.BigInteger(), nullable=False),
    sa.Column('discount_amount', sa.BigInteger(), nullable=False),
    sa.Column('shipping_cost', sa.BigInteger(), nullable=False),
    sa.Column('total_amount', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('payment_status', sa.String(length=16), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.CheckConstraint("payment_status IN ('unpaid','partial','paid')", name='ck_purchase_payment_status'),
    sa.CheckConstraint("status IN ('draft','ordered','received','cancelled')", name='ck_purchase_status'),
    sa.CheckConstraint('subtotal >= 0 AND discount_amount >= 0 AND shipping_cost >= 0 AND total_amount >= 0 AND total_amount = subtotal + shipping_cost - discount_amount', name='ck_purchase_totals'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['supplier_id'], ['supplier_stores.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('purchase_number')
    )
    op.create_index(op.f('ix_purchases_purchase_date'), 'purchases', ['purchase_date'], unique=False)
    op.create_index(op.f('ix_purchases_status'), 'purchases', ['status'], unique=False)
    op.create_index(op.f('ix_purchases_supplier_id'), 'purchases', ['supplier_id'], unique=False)
    op.create_table('supplier_materials',
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('supplier_id', sa.Uuid(), nullable=False),
    sa.Column('listing_name', sa.String(length=150), nullable=False),
    sa.Column('listing_url', sa.String(length=2048), nullable=True),
    sa.Column('package_quantity', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('package_unit', sa.String(length=32), nullable=False),
    sa.Column('quantity_in_base_unit', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('listed_price', sa.BigInteger(), nullable=False),
    sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('listed_price >= 0 AND listed_price <= 999999999999999', name='ck_listing_price'),
    sa.CheckConstraint('package_quantity > 0 AND quantity_in_base_unit > 0', name='ck_listing_quantity'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['supplier_id'], ['supplier_stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supplier_materials_is_active'), 'supplier_materials', ['is_active'], unique=False)
    op.create_index(op.f('ix_supplier_materials_material_id'), 'supplier_materials', ['material_id'], unique=False)
    op.create_index(op.f('ix_supplier_materials_supplier_id'), 'supplier_materials', ['supplier_id'], unique=False)
    op.create_table('order_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('flower_id', sa.Uuid(), nullable=True),
    sa.Column('product_id', sa.Uuid(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('item_name_snapshot', sa.String(length=150), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.BigInteger(), nullable=False),
    sa.Column('subtotal', sa.BigInteger(), nullable=False),
    sa.Column('recipe_snapshot', sa.JSON(), nullable=True),
    sa.Column('labor_cost_snapshot', sa.Numeric(precision=38, scale=8), nullable=False),
    sa.Column('estimated_hpp_snapshot', sa.Numeric(precision=38, scale=8), nullable=True),
    sa.Column('cost_complete', sa.Boolean(), nullable=False),
    sa.CheckConstraint('(flower_id IS NOT NULL AND product_id IS NULL) OR (flower_id IS NULL AND product_id IS NOT NULL)', name='ck_order_items_reference'),
    sa.CheckConstraint('estimated_hpp_snapshot IS NULL OR (estimated_hpp_snapshot >= 0 AND estimated_hpp_snapshot <= 999999999999999999999999999999.99999999)', name='ck_order_items_hpp'),
    sa.CheckConstraint('labor_cost_snapshot >= 0 AND labor_cost_snapshot <= 999999999999999999999999999999.99999999', name='ck_order_items_labor'),
    sa.CheckConstraint('quantity >= 1 AND quantity <= 1000000', name='ck_order_items_quantity'),
    sa.CheckConstraint('subtotal = quantity * unit_price', name='ck_order_items_subtotal'),
    sa.CheckConstraint('unit_price >= 0 AND unit_price <= 999999999999999 AND subtotal >= 0 AND subtotal <= 999999999999999', name='ck_order_items_amounts'),
    sa.ForeignKeyConstraint(['flower_id'], ['flowers.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_table('order_payments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('payment_key', sa.Uuid(), nullable=False),
    sa.Column('payment_date', sa.Date(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('method', sa.String(length=50), nullable=True),
    sa.Column('reference_number', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('amount > 0 AND amount <= 999999999999999', name='ck_order_payments_amount'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id', 'payment_key', name='uq_order_payment_key')
    )
    op.create_index(op.f('ix_order_payments_order_id'), 'order_payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_payments_payment_date'), 'order_payments', ['payment_date'], unique=False)
    op.create_table('production_records',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('order_id', sa.Uuid(), nullable=False),
    sa.Column('actual_material_cost', sa.Numeric(precision=38, scale=8), nullable=False),
    sa.Column('labor_cost_snapshot', sa.Numeric(precision=38, scale=8), nullable=False),
    sa.Column('total_production_cost', sa.Numeric(precision=38, scale=8), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('actual_material_cost >= 0 AND actual_material_cost <= 999999999999999999999999999999.99999999 AND labor_cost_snapshot >= 0 AND labor_cost_snapshot <= 999999999999999999999999999999.99999999 AND total_production_cost >= 0 AND total_production_cost <= 999999999999999999999999999999.99999999', name='ck_production_costs'),
    sa.CheckConstraint('total_production_cost = actual_material_cost + labor_cost_snapshot', name='ck_production_cost_matches'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    op.create_table('purchase_items',
    sa.Column('purchase_id', sa.Uuid(), nullable=False),
    sa.Column('material_id', sa.Uuid(), nullable=False),
    sa.Column('supplier_listing_id', sa.Uuid(), nullable=True),
    sa.Column('material_name_snapshot', sa.String(length=150), nullable=False),
    sa.Column('base_unit_snapshot', sa.String(length=32), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('quantity_base', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('unit_price', sa.BigInteger(), nullable=False),
    sa.Column('subtotal', sa.BigInteger(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint('quantity > 0 AND quantity_base > 0 AND unit_price >= 0 AND subtotal >= 0', name='ck_purchase_item_values'),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['supplier_listing_id'], ['supplier_materials.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_items_material_id'), 'purchase_items', ['material_id'], unique=False)
    op.create_index(op.f('ix_purchase_items_purchase_id'), 'purchase_items', ['purchase_id'], unique=False)
    op.create_table('purchase_payments',
    sa.Column('purchase_id', sa.Uuid(), nullable=False),
    sa.Column('payment_key', sa.Uuid(), nullable=False),
    sa.Column('payment_date', sa.Date(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('method', sa.String(length=50), nullable=True),
    sa.Column('reference_number', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint('amount > 0 AND amount <= 999999999999999', name='ck_purchase_payment_amount'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('purchase_id', 'payment_key', name='uq_purchase_payment_key')
    )
    op.create_index(op.f('ix_purchase_payments_payment_date'), 'purchase_payments', ['payment_date'], unique=False)
    op.create_index(op.f('ix_purchase_payments_purchase_id'), 'purchase_payments', ['purchase_id'], unique=False)
    op.add_column('users', sa.Column('full_name', sa.String(length=120), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=254), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(length=16), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('created_by', sa.Uuid(), nullable=True))
    op.drop_index(op.f('uq_users_single_superadmin'), table_name='users', postgresql_where='(is_superadmin = true)')
    op.create_index('uq_users_email_lower', 'users', [sa.literal_column('lower(email)')], unique=True)
    op.execute("UPDATE users SET full_name=username, email=username || '@legacy.invalid', role=CASE WHEN is_superadmin THEN 'superadmin' ELSE 'staff' END, is_active=true, updated_at=created_at")
    for name in ('full_name','email','role','is_active','updated_at'):
        op.alter_column('users',name,nullable=False)
    op.create_foreign_key('fk_users_created_by', 'users', 'users', ['created_by'], ['id'])
    op.create_check_constraint('ck_users_role','users',"role IN ('staff','superadmin')")
    op.create_check_constraint('ck_users_role_compatibility','users',"is_superadmin = (role = 'superadmin')")
    _copy_legacy_research()
    tables=('flowers','materials','products','supplier_stores','audit_logs','flower_materials','inventory_balances','inventory_movements','orders','product_flowers','product_materials','purchases','supplier_materials','order_items','order_payments','production_records','purchase_items','purchase_payments')
    for name in tables:
        op.execute(f'ALTER TABLE {name} ENABLE ROW LEVEL SECURITY')
        op.execute(f'REVOKE ALL ON TABLE {name} FROM PUBLIC, anon, authenticated, service_role')


def _copy_legacy_research():
    bind=op.get_bind()
    metadata=sa.MetaData()
    names=('suppliers','materials','supplier_stores','supplier_materials','inventory_balances')
    source,materials,stores,listings,balances=(sa.Table(name,metadata,autoload_with=bind) for name in names)
    namespace=UUID('9b93bd09-6621-4edf-947f-e1ff21adc18d')
    seen_materials=set()
    seen_stores=set()
    for row in bind.execute(sa.select(source)).mappings():
        key='|'.join(str(row[field] or '').strip().casefold() for field in ('material_name','variant','unit','category'))
        material_id=uuid5(namespace,'material:'+key)
        store_key='|'.join(str(row[field] or '').strip().casefold() for field in ('store_name','marketplace'))
        supplier_id=uuid5(namespace,'store:'+store_key)
        if material_id not in seen_materials:
            name=row['material_name']+(f" - {row['variant']}" if row['variant'] else '')
            bind.execute(materials.insert().values(id=material_id,sku='LEGACY-'+material_id.hex[:20].upper(),name=name[:150],category=row['category'],description=name,base_unit=row['unit'],minimum_stock=0,is_active=True,created_at=row['created_at'],updated_at=row['updated_at']))
            bind.execute(balances.insert().values(material_id=material_id,quantity_on_hand=0,average_unit_cost=0,has_received_cost=False,updated_at=row['updated_at']))
            seen_materials.add(material_id)
        if supplier_id not in seen_stores:
            platform=(row['marketplace'] or 'other').lower()
            platform=platform if platform in {'shopee','tokopedia','tiktok','offline','other'} else 'other'
            bind.execute(stores.insert().values(id=supplier_id,name=row['store_name'],platform=platform,is_active=True,notes='Imported legacy research; source retained.',created_at=row['created_at'],updated_at=row['updated_at']))
            seen_stores.add(supplier_id)
        checked=datetime.combine(row['last_checked_at'],time.min,ZoneInfo('Asia/Jakarta')).astimezone(UTC)
        bind.execute(listings.insert().values(id=row['id'],material_id=material_id,supplier_id=supplier_id,listing_name=row['material_name'],listing_url=row['purchase_url'],package_quantity=row['pack_quantity'],package_unit=row['unit'],quantity_in_base_unit=row['pack_quantity'],listed_price=int(row['price'].quantize(Decimal('1'),rounding=ROUND_HALF_UP)),last_checked_at=checked,notes=row['notes'],is_active=True,created_at=row['created_at'],updated_at=row['updated_at']))


def downgrade() -> None:
    bind=op.get_bind()
    # Do not silently discard transactions/catalogue data written since upgrade.
    for table in ('purchases','orders','inventory_movements','flowers','products','audit_logs'):
        if bind.scalar(sa.text(f'SELECT count(*) FROM {table}')):
            raise RuntimeError('Downgrade refused: preserve new business data and use documented restore/fix-forward procedure.')
    op.drop_constraint('ck_users_role_compatibility','users',type_='check')
    op.drop_constraint('ck_users_role','users',type_='check')
    op.drop_constraint('fk_users_created_by', 'users', type_='foreignkey')
    op.drop_index('uq_users_email_lower', table_name='users')
    op.create_index(op.f('uq_users_single_superadmin'), 'users', ['is_superadmin'], unique=True, postgresql_where='(is_superadmin = true)')
    op.drop_column('users', 'created_by')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'email')
    op.drop_column('users', 'full_name')
    op.drop_index(op.f('ix_purchase_payments_purchase_id'), table_name='purchase_payments')
    op.drop_index(op.f('ix_purchase_payments_payment_date'), table_name='purchase_payments')
    op.drop_table('purchase_payments')
    op.drop_index(op.f('ix_purchase_items_purchase_id'), table_name='purchase_items')
    op.drop_index(op.f('ix_purchase_items_material_id'), table_name='purchase_items')
    op.drop_table('purchase_items')
    op.drop_table('production_records')
    op.drop_index(op.f('ix_order_payments_payment_date'), table_name='order_payments')
    op.drop_index(op.f('ix_order_payments_order_id'), table_name='order_payments')
    op.drop_table('order_payments')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_supplier_materials_supplier_id'), table_name='supplier_materials')
    op.drop_index(op.f('ix_supplier_materials_material_id'), table_name='supplier_materials')
    op.drop_index(op.f('ix_supplier_materials_is_active'), table_name='supplier_materials')
    op.drop_table('supplier_materials')
    op.drop_index(op.f('ix_purchases_supplier_id'), table_name='purchases')
    op.drop_index(op.f('ix_purchases_status'), table_name='purchases')
    op.drop_index(op.f('ix_purchases_purchase_date'), table_name='purchases')
    op.drop_table('purchases')
    op.drop_index(op.f('ix_product_materials_product_id'), table_name='product_materials')
    op.drop_index(op.f('ix_product_materials_material_id'), table_name='product_materials')
    op.drop_table('product_materials')
    op.drop_index(op.f('ix_product_flowers_product_id'), table_name='product_flowers')
    op.drop_index(op.f('ix_product_flowers_flower_id'), table_name='product_flowers')
    op.drop_table('product_flowers')
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_sales_channel'), table_name='orders')
    op.drop_index(op.f('ix_orders_required_date'), table_name='orders')
    op.drop_index(op.f('ix_orders_payment_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_order_date'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_name'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_inventory_movements_reference_type'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_reference_id'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_material_id'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_created_at'), table_name='inventory_movements')
    op.drop_table('inventory_movements')
    op.drop_table('inventory_balances')
    op.drop_index(op.f('ix_flower_materials_material_id'), table_name='flower_materials')
    op.drop_index(op.f('ix_flower_materials_flower_id'), table_name='flower_materials')
    op.drop_table('flower_materials')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_actor_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_supplier_stores_platform'), table_name='supplier_stores')
    op.drop_index(op.f('ix_supplier_stores_name'), table_name='supplier_stores')
    op.drop_index(op.f('ix_supplier_stores_is_active'), table_name='supplier_stores')
    op.drop_table('supplier_stores')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_is_active'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_materials_name'), table_name='materials')
    op.drop_index(op.f('ix_materials_is_active'), table_name='materials')
    op.drop_index(op.f('ix_materials_category'), table_name='materials')
    op.drop_table('materials')
    op.drop_index(op.f('ix_flowers_name'), table_name='flowers')
    op.drop_index(op.f('ix_flowers_is_active'), table_name='flowers')
    op.drop_index(op.f('ix_flowers_category'), table_name='flowers')
    op.drop_table('flowers')
    # ### end Alembic commands ###
