"""PRD v2 internal custom bouquets and cash finance; no public endpoints.

Revision ID: 20261017_06
Revises: 20261015_05

New table DDL is frozen here; future ORM edits do not change this revision.
Old payment accounts remain NULL until explicitly validated through backfill.
"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid5,NAMESPACE_URL

revision='20261017_06'
down_revision='20261015_05'
branch_labels=None
depends_on=None

NEW_TABLES = ['bouquet_options', 'bouquet_settings', 'expense_categories', 'bouquet_option_materials', 'cash_accounts', 'cash_operations', 'custom_bouquets', 'operating_expenses', 'cash_transactions', 'custom_bouquet_flowers', 'custom_bouquet_materials', 'custom_bouquet_options', 'expense_payments', 'expense_receipts']
DDL = (
    """CREATE TABLE bouquet_options (
	name VARCHAR(150) NOT NULL, 
	option_group VARCHAR(32) NOT NULL, 
	description TEXT, 
	image_url VARCHAR(2048), 
	selling_price BIGINT NOT NULL, 
	min_quantity INTEGER NOT NULL, 
	max_quantity INTEGER NOT NULL, 
	requires_materials BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_bouquet_option_bounds CHECK (selling_price BETWEEN 0 AND 999999999999999 AND min_quantity >= 1 AND max_quantity >= min_quantity AND max_quantity <= 1000000), 
	CONSTRAINT ck_bouquet_option_group CHECK (option_group IN ('wrapping','ribbon','greeting_card','accessory'))
)""",
    """CREATE TABLE bouquet_settings (
	id INTEGER NOT NULL, 
	min_stems INTEGER NOT NULL, 
	max_stems INTEGER NOT NULL, 
	minimum_price BIGINT NOT NULL, 
	assembly_fee BIGINT NOT NULL, 
	assembly_labor_cost NUMERIC(38, 8) NOT NULL, 
	pricing_version INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_bouquet_settings_bounds CHECK (id = 1 AND min_stems >= 1 AND max_stems >= min_stems AND max_stems <= 1000000 AND minimum_price BETWEEN 0 AND 999999999999999 AND assembly_fee BETWEEN 0 AND 999999999999999 AND assembly_labor_cost >= 0 AND assembly_labor_cost < 1000000000000000000000000000000 AND pricing_version >= 1)
)""",
    """CREATE TABLE expense_categories (
	id UUID NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	classification VARCHAR(24) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_expense_category_classification CHECK (classification IN ('operational','equipment','other')), 
	UNIQUE (name)
)""",
    """CREATE TABLE bouquet_option_materials (
	bouquet_option_id UUID NOT NULL, 
	material_id UUID NOT NULL, 
	quantity_required NUMERIC(20, 6) NOT NULL, 
	unit VARCHAR(32) NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_bouquet_option_material UNIQUE (bouquet_option_id, material_id), 
	CONSTRAINT ck_bouquet_option_material_quantity CHECK (quantity_required > 0 AND quantity_required <= 999999999999.999999), 
	FOREIGN KEY(bouquet_option_id) REFERENCES bouquet_options (id) ON DELETE CASCADE, 
	FOREIGN KEY(material_id) REFERENCES materials (id) ON DELETE RESTRICT
)""",
    """CREATE INDEX ix_bouquet_option_materials_bouquet_option_id ON bouquet_option_materials (bouquet_option_id)""",
    """CREATE TABLE cash_accounts (
	id UUID NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	account_type VARCHAR(16) NOT NULL, 
	opening_date DATE NOT NULL, 
	history_mode VARCHAR(16) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_cash_account_type CHECK (account_type IN ('cash','bank','e_wallet')), 
	CONSTRAINT ck_cash_account_history_mode CHECK (history_mode IN ('opening','backfill')), 
	CONSTRAINT ck_cash_account_name CHECK (length(trim(name)) > 0), 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
)""",
    """CREATE TABLE cash_operations (
	operation_key UUID NOT NULL, 
	kind VARCHAR(32) NOT NULL, 
	request_payload JSON NOT NULL, 
	result JSON NOT NULL, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (operation_key), 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
)""",
    """CREATE TABLE custom_bouquets (
	configuration_number VARCHAR(40) NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	customer_reference VARCHAR(150), 
	description TEXT, 
	image_reference VARCHAR(2048), 
	personalization JSON NOT NULL, 
	estimated_hpp NUMERIC(38, 8), 
	cost_complete BOOLEAN NOT NULL, 
	proposed_price BIGINT NOT NULL, 
	final_price BIGINT, 
	price_override_reason TEXT, 
	assembly_fee BIGINT NOT NULL, 
	assembly_labor_cost NUMERIC(38, 8) NOT NULL, 
	pricing_version INTEGER NOT NULL, 
	recipe_snapshot JSON NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_custom_bouquet_status CHECK (status IN ('draft','finalized','archived')), 
	CONSTRAINT ck_custom_bouquet_amounts CHECK (proposed_price BETWEEN 0 AND 999999999999999 AND (final_price IS NULL OR final_price BETWEEN 0 AND 999999999999999) AND assembly_fee BETWEEN 0 AND 999999999999999 AND assembly_labor_cost >= 0 AND assembly_labor_cost < 1000000000000000000000000000000 AND (estimated_hpp IS NULL OR (estimated_hpp >= 0 AND estimated_hpp < 1000000000000000000000000000000))), 
	UNIQUE (configuration_number), 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(updated_by) REFERENCES users (id) ON DELETE SET NULL
)""",
    """CREATE TABLE operating_expenses (
	id UUID NOT NULL, 
	expense_number VARCHAR(50) NOT NULL, 
	category_id UUID NOT NULL, 
	title VARCHAR(150) NOT NULL, 
	description TEXT, 
	vendor_name VARCHAR(150), 
	expense_date DATE NOT NULL, 
	amount BIGINT NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	payment_status VARCHAR(16) NOT NULL, 
	created_by UUID NOT NULL, 
	posted_by UUID, 
	posted_at TIMESTAMP WITH TIME ZONE, 
	voided_by UUID, 
	voided_at TIMESTAMP WITH TIME ZONE, 
	void_reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_operating_expense_amount CHECK (amount > 0 AND amount <= 999999999999999), 
	CONSTRAINT ck_operating_expense_status CHECK (status IN ('draft','posted','void')), 
	CONSTRAINT ck_operating_expense_payment_status CHECK (payment_status IN ('unpaid','partial','paid')), 
	UNIQUE (expense_number), 
	FOREIGN KEY(category_id) REFERENCES expense_categories (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(posted_by) REFERENCES users (id), 
	FOREIGN KEY(voided_by) REFERENCES users (id)
)""",
    """CREATE INDEX ix_operating_expenses_category_id ON operating_expenses (category_id)""",
    """CREATE INDEX ix_operating_expenses_created_by ON operating_expenses (created_by)""",
    """CREATE INDEX ix_operating_expenses_expense_date ON operating_expenses (expense_date)""",
    """CREATE INDEX ix_operating_expenses_payment_status ON operating_expenses (payment_status)""",
    """CREATE INDEX ix_operating_expenses_status ON operating_expenses (status)""",
    """CREATE TABLE cash_transactions (
	id UUID NOT NULL, 
	transaction_number VARCHAR(48) NOT NULL, 
	cash_account_id UUID NOT NULL, 
	transaction_date DATE NOT NULL, 
	direction VARCHAR(3) NOT NULL, 
	amount BIGINT NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	source_type VARCHAR(32) NOT NULL, 
	source_id UUID NOT NULL, 
	description TEXT, 
	operation_key UUID, 
	reversal_of_id UUID, 
	created_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_cash_source UNIQUE (source_type, source_id), 
	CONSTRAINT ck_cash_direction CHECK (direction IN ('IN','OUT')), 
	CONSTRAINT ck_cash_amount CHECK (amount > 0 AND amount <= 999999999999999), 
	UNIQUE (transaction_number), 
	FOREIGN KEY(cash_account_id) REFERENCES cash_accounts (id) ON DELETE RESTRICT, 
	FOREIGN KEY(operation_key) REFERENCES cash_operations (operation_key) ON DELETE RESTRICT, 
	UNIQUE (reversal_of_id), 
	FOREIGN KEY(reversal_of_id) REFERENCES cash_transactions (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
)""",
    """CREATE INDEX ix_cash_account_chronology ON cash_transactions (cash_account_id, transaction_date, created_at, id)""",
    """CREATE INDEX ix_cash_transactions_category ON cash_transactions (category)""",
    """CREATE INDEX ix_cash_transactions_operation_key ON cash_transactions (operation_key)""",
    """CREATE INDEX ix_cash_transactions_transaction_date ON cash_transactions (transaction_date)""",
    """CREATE TABLE custom_bouquet_flowers (
	custom_bouquet_id UUID NOT NULL, 
	flower_id UUID NOT NULL, 
	quantity INTEGER NOT NULL, 
	estimated_hpp_snapshot NUMERIC(38, 8), 
	unit_price_snapshot BIGINT NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_custom_bouquet_flower UNIQUE (custom_bouquet_id, flower_id), 
	CONSTRAINT ck_custom_bouquet_flower_hpp CHECK (estimated_hpp_snapshot IS NULL OR (estimated_hpp_snapshot >= 0 AND estimated_hpp_snapshot < 1000000000000000000000000000000)), 
	CONSTRAINT ck_custom_bouquet_flower_bounds CHECK (quantity BETWEEN 1 AND 1000000 AND unit_price_snapshot BETWEEN 0 AND 999999999999999), 
	FOREIGN KEY(custom_bouquet_id) REFERENCES custom_bouquets (id) ON DELETE CASCADE, 
	FOREIGN KEY(flower_id) REFERENCES flowers (id) ON DELETE RESTRICT
)""",
    """CREATE INDEX ix_custom_bouquet_flowers_custom_bouquet_id ON custom_bouquet_flowers (custom_bouquet_id)""",
    """CREATE TABLE custom_bouquet_materials (
	custom_bouquet_id UUID NOT NULL, 
	material_id UUID NOT NULL, 
	quantity_required NUMERIC(20, 6) NOT NULL, 
	unit VARCHAR(32) NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_custom_bouquet_material UNIQUE (custom_bouquet_id, material_id), 
	CONSTRAINT ck_custom_bouquet_material_quantity CHECK (quantity_required > 0 AND quantity_required <= 999999999999.999999), 
	FOREIGN KEY(custom_bouquet_id) REFERENCES custom_bouquets (id) ON DELETE CASCADE, 
	FOREIGN KEY(material_id) REFERENCES materials (id) ON DELETE RESTRICT
)""",
    """CREATE INDEX ix_custom_bouquet_materials_custom_bouquet_id ON custom_bouquet_materials (custom_bouquet_id)""",
    """CREATE TABLE custom_bouquet_options (
	custom_bouquet_id UUID NOT NULL, 
	bouquet_option_id UUID NOT NULL, 
	quantity INTEGER NOT NULL, 
	selling_price_snapshot BIGINT NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_custom_bouquet_option UNIQUE (custom_bouquet_id, bouquet_option_id), 
	CONSTRAINT ck_custom_bouquet_option_bounds CHECK (quantity BETWEEN 1 AND 1000000 AND selling_price_snapshot BETWEEN 0 AND 999999999999999), 
	FOREIGN KEY(custom_bouquet_id) REFERENCES custom_bouquets (id) ON DELETE CASCADE, 
	FOREIGN KEY(bouquet_option_id) REFERENCES bouquet_options (id) ON DELETE RESTRICT
)""",
    """CREATE INDEX ix_custom_bouquet_options_custom_bouquet_id ON custom_bouquet_options (custom_bouquet_id)""",
    """CREATE TABLE expense_payments (
	id UUID NOT NULL, 
	expense_id UUID NOT NULL, 
	payment_key UUID NOT NULL, 
	cash_account_id UUID NOT NULL, 
	payment_date DATE NOT NULL, 
	amount BIGINT NOT NULL, 
	method VARCHAR(50) NOT NULL, 
	reference_number VARCHAR(100), 
	notes TEXT, 
	proof_url VARCHAR(2048), 
	reversed_at TIMESTAMP WITH TIME ZONE, 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_expense_payment_amount CHECK (amount > 0 AND amount <= 999999999999999), 
	FOREIGN KEY(expense_id) REFERENCES operating_expenses (id), 
	UNIQUE (payment_key), 
	FOREIGN KEY(cash_account_id) REFERENCES cash_accounts (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
)""",
    """CREATE INDEX ix_expense_payments_cash_account_id ON expense_payments (cash_account_id)""",
    """CREATE INDEX ix_expense_payments_expense_id ON expense_payments (expense_id)""",
    """CREATE INDEX ix_expense_payments_payment_date ON expense_payments (payment_date)""",
    """CREATE TABLE expense_receipts (
	id UUID NOT NULL, 
	expense_id UUID NOT NULL, 
	storage_name VARCHAR(50) NOT NULL, 
	mime_type VARCHAR(50) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	original_name VARCHAR(200) NOT NULL, 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(expense_id) REFERENCES operating_expenses (id) ON DELETE CASCADE, 
	UNIQUE (storage_name), 
	FOREIGN KEY(created_by) REFERENCES users (id)
)""",
    """CREATE INDEX ix_expense_receipts_expense_id ON expense_receipts (expense_id)""",
)


def upgrade():
    for statement in DDL:
        op.execute(statement)
    for name in NEW_TABLES:
        op.execute(f'ALTER TABLE "{name}" ENABLE ROW LEVEL SECURITY')
        op.execute(f'REVOKE ALL ON TABLE "{name}" FROM PUBLIC, anon, authenticated, service_role')
    for table in ('order_payments','purchase_payments'):
        op.add_column(table,sa.Column('cash_account_id',sa.Uuid(),nullable=True))
        op.add_column(table,sa.Column('reversed_at',sa.DateTime(timezone=True),nullable=True))
        op.create_foreign_key('fk_'+table+'_cash_account',table,'cash_accounts',['cash_account_id'],['id'],ondelete='RESTRICT')
        op.create_index('ix_'+table+'_cash_account_id',table,['cash_account_id'])
    op.add_column('order_items',sa.Column('custom_bouquet_id',sa.Uuid(),nullable=True))
    op.add_column('order_items',sa.Column('item_type',sa.String(32),nullable=True))
    op.execute("UPDATE order_items SET item_type=CASE WHEN product_id IS NOT NULL THEN 'PRODUCT' ELSE 'FLOWER' END")
    op.alter_column('order_items','item_type',nullable=False)
    op.create_foreign_key('fk_order_items_custom_bouquet','order_items','custom_bouquets',['custom_bouquet_id'],['id'],ondelete='RESTRICT')
    op.drop_constraint('ck_order_items_reference','order_items',type_='check')
    op.create_check_constraint('ck_order_items_reference',"order_items",'(flower_id IS NOT NULL AND product_id IS NULL AND custom_bouquet_id IS NULL) OR (flower_id IS NULL AND product_id IS NOT NULL AND custom_bouquet_id IS NULL) OR (flower_id IS NULL AND product_id IS NULL AND custom_bouquet_id IS NOT NULL)')
    op.create_check_constraint('ck_order_items_type',"order_items","(custom_bouquet_id IS NOT NULL AND item_type = 'CUSTOM_BOUQUET') OR (product_id IS NOT NULL AND item_type = 'PRODUCT') OR (flower_id IS NOT NULL AND item_type = 'FLOWER')")
    categories=[('Marketing','operational'),('Transportation','operational'),('Utilities','operational'),('Operational','operational'),('Shipping','operational'),('Equipment','equipment'),('Miscellaneous','other')]
    for name,classification in categories:
        op.get_bind().execute(sa.text('INSERT INTO expense_categories (id,name,description,classification,is_active) VALUES (:id,:name,NULL,:classification,true)'),{'id':uuid5(NAMESPACE_URL,'florist-expense-category:'+name),'name':name,'classification':classification})
    op.execute('INSERT INTO bouquet_settings (id,min_stems,max_stems,minimum_price,assembly_fee,assembly_labor_cost,pricing_version) VALUES (1,1,1000,0,0,0,1)')
    op.execute("""CREATE FUNCTION reject_cash_transaction_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'Cash ledger is append-only; record a reversal instead.' USING ERRCODE='23514'; END; $$""")
    op.execute('CREATE TRIGGER cash_transactions_append_only BEFORE UPDATE OR DELETE ON cash_transactions FOR EACH ROW EXECUTE FUNCTION reject_cash_transaction_mutation()')


def downgrade():
    # Never silently discard operational or financial records during rollback.
    expected={'Marketing':'operational','Transportation':'operational','Utilities':'operational','Operational':'operational','Shipping':'operational','Equipment':'equipment','Miscellaneous':'other'}
    for row in op.get_bind().execute(sa.text('SELECT id,name,description,classification,is_active FROM expense_categories')).mappings():
        if row['name'] not in expected or str(row['id'])!=str(uuid5(NAMESPACE_URL,'florist-expense-category:'+row['name'])) or row['classification']!=expected[row['name']] or row['description'] is not None or not row['is_active']:
            raise RuntimeError('Rollback refused: expense categories were customized.')
    if op.get_bind().scalar(sa.text('SELECT count(*) FROM bouquet_settings WHERE id<>1 OR min_stems<>1 OR max_stems<>1000 OR minimum_price<>0 OR assembly_fee<>0 OR assembly_labor_cost<>0 OR pricing_version<>1')):
        raise RuntimeError('Rollback refused: bouquet settings were customized.')
    for name in NEW_TABLES:
        if name not in ('bouquet_settings','expense_categories') and op.get_bind().scalar(sa.text(f'SELECT count(*) FROM "{name}"')):
            raise RuntimeError('Rollback refused: PRD v2 data exists. Restore a reviewed backup or retain the expanded schema.')
    if op.get_bind().scalar(sa.text('SELECT count(*) FROM order_items WHERE custom_bouquet_id IS NOT NULL')):
        raise RuntimeError('Rollback refused: custom order history exists.')
    op.execute('DROP TRIGGER cash_transactions_append_only ON cash_transactions')
    op.execute('DROP FUNCTION reject_cash_transaction_mutation()')
    op.drop_constraint('ck_order_items_type','order_items',type_='check')
    op.drop_constraint('ck_order_items_reference','order_items',type_='check')
    op.create_check_constraint('ck_order_items_reference','order_items','(flower_id IS NOT NULL AND product_id IS NULL) OR (flower_id IS NULL AND product_id IS NOT NULL)')
    op.drop_constraint('fk_order_items_custom_bouquet','order_items',type_='foreignkey')
    op.drop_column('order_items','custom_bouquet_id')
    op.drop_column('order_items','item_type')
    for table in ('order_payments','purchase_payments'):
        op.drop_index('ix_'+table+'_cash_account_id',table)
        op.drop_constraint('fk_'+table+'_cash_account',table,type_='foreignkey')
        op.drop_column(table,'reversed_at')
        op.drop_column(table,'cash_account_id')
    for name in reversed(NEW_TABLES):
        op.drop_table(name)
