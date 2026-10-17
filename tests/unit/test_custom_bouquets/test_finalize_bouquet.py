import importlib.util
import unittest
from fastapi import HTTPException

class FinalizeBouquetTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("use_cases.custom_bouquets"), "Custom bouquet lifecycle is missing")
        from tests.unit.test_custom_bouquets.support import setup_bouquet
        setup_bouquet(self)

    def test_override_requires_admin_reason_and_audit(self):
        from use_cases.custom_bouquets.create_bouquet import create_bouquet
        from use_cases.custom_bouquets.finalize_bouquet import finalize_bouquet
        from schemas.custom_bouquet_schema import BouquetFinalize
        from models.audit_log_model import AuditLog
        from sqlalchemy import select
        row=create_bouquet(self.db,self.staff,self.data)
        for actor,data,code in ((self.staff,BouquetFinalize(final_price=500,reason="Deal"),403),(self.admin,BouquetFinalize(final_price=500),422)):
            with self.assertRaises(HTTPException) as error: finalize_bouquet(self.db,actor,row.id,data)
            self.assertEqual(error.exception.status_code,code)
        row=finalize_bouquet(self.db,self.admin,row.id,BouquetFinalize(final_price=500,reason="Deal"))
        self.assertEqual(row.final_price,500)
        self.assertEqual(row.estimated_hpp,90)
        self.assertTrue(any(r.action=="price_override" for r in self.db.scalars(select(AuditLog))))
