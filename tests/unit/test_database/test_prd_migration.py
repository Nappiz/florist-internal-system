import importlib.util
import os
import re
import unittest
from pathlib import Path
from uuid import uuid4
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.schema import CreateSchema,DropSchema
from configs.database import get_engine


@unittest.skipUnless(os.getenv('RUN_POSTGRES_SECURITY_TESTS')=='1','Opt-in PostgreSQL migration rehearsal uses a temporary schema.')
class PrdMigrationTests(unittest.TestCase):
    def test_legacy_upgrade_copy_and_rollback_preserve_source(self):
        schema='migration_verify_'+uuid4().hex[:12]
        self.assertRegex(schema,r'^migration_verify_[a-f0-9]{12}$')
        engine=get_engine()
        root=Path(__file__).resolve().parents[3]
        revisions=[]
        for name in ('a11c6331bb7c_prd_catalogue_purchasing_production_.py','20261015_05_inventory_bounds.py'):
            spec=importlib.util.spec_from_file_location('migration_under_test',root/'migration'/'versions'/name)
            module=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            revisions.append(module)
        try:
            with engine.begin() as connection:
                connection.execute(CreateSchema(schema))
                connection.exec_driver_sql(f'REVOKE ALL ON SCHEMA "{schema}" FROM PUBLIC, anon, authenticated, service_role')
                connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
                # LIKE copies definitions only, never business/credential rows.
                for table in ('users','auth_sessions','login_throttles','suppliers','expenses'):
                    connection.exec_driver_sql(f'CREATE TABLE "{schema}"."{table}" (LIKE public."{table}" INCLUDING ALL)')
                for column in ('full_name','email','role','is_active','updated_at','last_login','created_by'):
                    connection.exec_driver_sql(f'ALTER TABLE users DROP COLUMN "{column}"')
                connection.exec_driver_sql('CREATE UNIQUE INDEX uq_users_single_superadmin ON users (is_superadmin) WHERE is_superadmin=true')
                user_id=uuid4()
                source_id=uuid4()
                connection.execute(text("INSERT INTO users (id,username,password_hash,is_superadmin,credential_version,created_at) VALUES (:id,'migration_admin','test-only-not-a-real-hash',true,0,now())"),{'id':user_id})
                connection.execute(text("INSERT INTO suppliers (id,material_name,store_name,purchase_url,price,pack_quantity,unit,last_checked_at,created_at,updated_at,created_by) VALUES (:id,'Migration material','Migration shop','https://example.com/item',1234.50,100,'pcs','2026-10-15',now(),now(),:actor)"),{'id':source_id,'actor':user_id})
                with Operations.context(MigrationContext.configure(connection)):
                    for revision in revisions: revision.upgrade()
                    self.assertEqual(connection.scalar(text('SELECT count(*) FROM supplier_materials')),1)
                    self.assertEqual(connection.scalar(text('SELECT listed_price FROM supplier_materials')),1235)
                    self.assertEqual(connection.scalar(text('SELECT price FROM suppliers')),1234.50)
                    self.assertEqual(connection.scalar(text('SELECT quantity_on_hand FROM inventory_balances')),0)
                    self.assertEqual(connection.scalar(text('SELECT role FROM users')),'superadmin')
                    self.assertTrue(connection.scalar(text("SELECT relrowsecurity FROM pg_class WHERE oid='inventory_movements'::regclass")))
                    for revision in reversed(revisions): revision.downgrade()
                self.assertEqual(connection.scalar(text('SELECT count(*) FROM suppliers')),1)
                self.assertEqual(connection.scalar(text('SELECT count(*) FROM users')),1)
                self.assertIsNone(connection.scalar(text("SELECT to_regclass('purchases')")))
        finally:
            if re.fullmatch(r'migration_verify_[a-f0-9]{12}',schema) is None: raise RuntimeError('Unexpected temporary migration schema')
            with engine.begin() as connection:
                connection.execute(DropSchema(schema,cascade=True,if_exists=True))
