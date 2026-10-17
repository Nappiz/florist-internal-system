import importlib.util
import os
import unittest
from datetime import UTC,date,datetime
from pathlib import Path
from uuid import uuid4
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import MetaData,Table,text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.schema import CreateSchema,DropSchema
from configs.database import get_engine
from models import Base

@unittest.skipUnless(os.getenv("RUN_POSTGRES_SECURITY_TESTS")=="1","Opt-in temporary PostgreSQL migration schema")
class GrowthFinanceMigrationTests(unittest.TestCase):
    def test_upgrade_preserves_payments_guards_ledger_and_clean_rollback(self):
        name="growth_verify_"+uuid4().hex[:12]
        self.assertRegex(name,r"^growth_verify_[a-f0-9]{12}$")
        root=Path(__file__).resolve().parents[3]
        spec=importlib.util.spec_from_file_location("growth_revision",root/"migration/versions/20261017_06_growth_finance.py")
        revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
        engine=get_engine()
        try:
            with engine.begin() as connection:
                connection.execute(CreateSchema(name))
                connection.exec_driver_sql(f'REVOKE ALL ON SCHEMA "{name}" FROM PUBLIC, anon, authenticated, service_role')
                connection.exec_driver_sql(f'SET LOCAL search_path TO "{name}"')
                for table in Base.metadata.tables:
                    if table not in revision.NEW_TABLES:
                        connection.exec_driver_sql(f'CREATE TABLE "{table}" (LIKE public."{table}" INCLUDING ALL)')
                # Reconstruct pre-v2 shape even after the live database is upgraded.
                for payment_table in ('order_payments','purchase_payments'):
                    connection.exec_driver_sql(f'ALTER TABLE "{payment_table}" DROP COLUMN IF EXISTS cash_account_id')
                    connection.exec_driver_sql(f'ALTER TABLE "{payment_table}" DROP COLUMN IF EXISTS reversed_at')
                connection.exec_driver_sql('ALTER TABLE order_items DROP CONSTRAINT IF EXISTS ck_order_items_type')
                connection.exec_driver_sql('ALTER TABLE order_items DROP CONSTRAINT IF EXISTS ck_order_items_reference')
                connection.exec_driver_sql('ALTER TABLE order_items DROP COLUMN IF EXISTS custom_bouquet_id')
                connection.exec_driver_sql('ALTER TABLE order_items DROP COLUMN IF EXISTS item_type')
                connection.exec_driver_sql('ALTER TABLE order_items ADD CONSTRAINT ck_order_items_reference CHECK ((flower_id IS NOT NULL AND product_id IS NULL) OR (flower_id IS NULL AND product_id IS NOT NULL))')
                # Reflected inserts use database-only old shape, never business rows.
                metadata=MetaData()
                order=Table('orders',metadata,autoload_with=connection)
                pay=Table('order_payments',metadata,autoload_with=connection)
                flower=Table('flowers',metadata,autoload_with=connection)
                item=Table('order_items',metadata,autoload_with=connection)
                now=datetime.now(UTC);order_id=uuid4();payment_id=uuid4();flower_id=uuid4()
                connection.execute(flower.insert().values(id=flower_id,sku='MIG-F',name='Migration flower',selling_price=100,estimated_labor_cost=0,is_active=True,created_at=now,updated_at=now))
                connection.execute(order.insert().values(id=order_id,order_number='MIG-ORDER',customer_name='Migration dummy',sales_channel='other',fulfillment_method='pickup',order_date=date(2026,10,1),subtotal=100,discount_amount=0,shipping_charge=0,total_amount=100,status='draft',payment_status='paid',created_at=now,updated_at=now))
                connection.execute(item.insert().values(id=uuid4(),order_id=order_id,flower_id=flower_id,position=0,item_name_snapshot='Migration flower',quantity=1,unit_price=100,subtotal=100,labor_cost_snapshot=0,cost_complete=False))
                connection.execute(pay.insert().values(id=payment_id,order_id=order_id,payment_key=uuid4(),payment_date=date(2026,10,1),amount=100,created_at=now))
                with Operations.context(MigrationContext.configure(connection)):
                    revision.upgrade()
                    self.assertEqual(connection.scalar(text('SELECT amount FROM order_payments WHERE id=:id'),{'id':payment_id}),100)
                    self.assertIsNone(connection.scalar(text('SELECT cash_account_id FROM order_payments WHERE id=:id'),{'id':payment_id}))
                    self.assertEqual(connection.scalar(text('SELECT item_type FROM order_items')),'FLOWER')
                    self.assertEqual(connection.scalar(text('SELECT count(*) FROM cash_transactions')),0)
                    self.assertEqual(connection.scalar(text('SELECT count(*) FROM expense_categories')),7)
                    for table in revision.NEW_TABLES:
                        self.assertTrue(connection.scalar(text('SELECT relrowsecurity FROM pg_class WHERE oid=to_regclass(:name)'),{'name':table}))
                    with connection.begin_nested() as fixture:
                        account_id=uuid4();transaction_id=uuid4()
                        connection.execute(text("INSERT INTO cash_accounts(id,name,account_type,opening_date,history_mode,is_active,created_at) VALUES (:id,'Test cash','cash','2020-01-01','backfill',true,now())"),{'id':account_id})
                        connection.execute(text("INSERT INTO cash_transactions(id,transaction_number,cash_account_id,transaction_date,direction,amount,category,source_type,source_id,created_at) VALUES (:id,'MIG-CASH',:account,'2026-10-01','IN',100,'correction','adjustment',:id,now())"),{'id':transaction_id,'account':account_id})
                        with connection.begin_nested() as mutation:
                            with self.assertRaises(DBAPIError):connection.execute(text('UPDATE cash_transactions SET amount=200'))
                            mutation.rollback()
                        with self.assertRaises(RuntimeError):revision.downgrade()
                        fixture.rollback()
                    revision.downgrade()
                    self.assertEqual(connection.scalar(text('SELECT amount FROM order_payments WHERE id=:id'),{'id':payment_id}),100)
                    self.assertIsNone(connection.scalar(text("SELECT to_regclass('cash_accounts')")))
                    revision.upgrade()
                    self.assertEqual(connection.scalar(text('SELECT count(*) FROM order_payments')),1)
        finally:
            with engine.begin() as connection:connection.execute(DropSchema(name,cascade=True,if_exists=True))
