import unittest
from uuid import uuid4
from pydantic import ValidationError
from schemas.order_schema import OrderPaymentCreate
from schemas.purchase_schema import PaymentInput

class PaymentContractTests(unittest.TestCase):
    def test_all_new_payments_require_explicit_account(self):
        for schema,values in ((OrderPaymentCreate,dict(payment_key=uuid4(),amount=1)),(PaymentInput,dict(payment_key=uuid4(),amount=1,payment_date="2026-10-01"))):
            with self.subTest(schema=schema.__name__), self.assertRaises(ValidationError):
                schema(**values)

    def test_payment_models_track_account_and_reversals(self):
        from models.order_payment_model import OrderPayment
        from models.purchase_payment_model import PurchasePayment
        for model in (OrderPayment,PurchasePayment):
            self.assertTrue(hasattr(model,"cash_account_id"))
            self.assertTrue(hasattr(model,"reversed_at"))
