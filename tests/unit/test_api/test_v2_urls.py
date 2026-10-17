import unittest
from uuid import uuid4
from pydantic import ValidationError
from schemas.custom_bouquet_schema import BouquetCreate
from schemas.bouquet_option_schema import BouquetOptionCreate
from schemas.operational_expense_schema import ExpensePaymentCreate

class PrivateModuleUrlTests(unittest.TestCase):
    def test_non_web_image_and_proof_schemes_are_rejected(self):
        for value in ['javascript:alert(1)','data:text/html,test','file:///private/file']:
            for schema,fields in [(BouquetCreate,{'image_reference':value}),(BouquetOptionCreate,{'name':'Wrap','option_group':'wrapping','selling_price':100,'image_url':value}),(ExpensePaymentCreate,{'payment_key':uuid4(),'cash_account_id':uuid4(),'payment_date':'2026-10-01','amount':100,'method':'cash','proof_url':value})]:
                with self.subTest(schema=schema.__name__,value=value),self.assertRaises(ValidationError):schema(**fields)
