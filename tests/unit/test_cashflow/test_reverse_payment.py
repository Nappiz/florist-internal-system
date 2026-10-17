from datetime import timedelta
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import func, select
from models import Order, OrderPayment
from models.cash_transaction_model import CashTransaction
from schemas.cashflow_schema import ReverseInput, CashflowQuery
from tests.unit.test_cashflow.base import CashTestCase
from use_cases.cashflow.post_payment import post_payment
from use_cases.cashflow.reverse_payment import reverse_payment
from use_cases.cashflow.summary import summary
from use_cases.cashflow.reconcile import reconcile


class ReversePaymentTests(CashTestCase):
    def paid_order(self):
        account = self.account(amount=0)
        order = Order(order_number='ORDER-' + uuid4().hex, customer_name='Test', order_date=self.day, subtotal=500, total_amount=500, payment_status='paid')
        self.db.add(order)
        self.db.flush()
        payment = OrderPayment(id=uuid4(), order_id=order.id, payment_key=uuid4(), payment_date=self.day, amount=500, cash_account_id=account['id'])
        self.db.add(payment)
        self.db.flush()
        row = post_payment(self.db, self.actor, 'order_payment', payment)
        self.db.commit()
        return order, payment, row

    def test_refund_preserves_original_and_reopens_balance_due_once(self):
        order, payment, original = self.paid_order()
        data = ReverseInput(operation_key=uuid4(), transaction_date=self.day + timedelta(days=1), reason='Verified refund')
        reversal = reverse_payment(self.db, self.actor, original.id, data)
        retry = reverse_payment(self.db, self.actor, original.id, data)
        self.assertEqual(reversal['id'], retry['id'])
        self.assertEqual((reversal['amount'], reversal['direction'], reversal['source_type']), (500, 'OUT', 'refund'))
        self.assertEqual(self.db.get(CashTransaction, original.id).amount, 500)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(CashTransaction)), 2)
        self.assertIsNotNone(payment.reversed_at)
        self.assertEqual(order.payment_status, 'unpaid')
        self.assertEqual(summary(self.db, self.actor, CashflowQuery())['closing_balance'], 0)
        self.assertTrue(reconcile(self.db, self.actor)['is_reconciled'])
        with self.assertRaises(HTTPException):
            reverse_payment(self.db, self.actor, original.id, data.model_copy(update={'operation_key': uuid4()}))

    def test_reconciliation_finds_amount_account_and_reversal_disagreements(self):
        _, payment, original = self.paid_order()
        payment.amount = 400
        self.db.commit()
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'amount_mismatch': 1})
        payment.amount = 500
        payment.cash_account_id = None
        self.db.commit()
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'unmapped_payment': 1})
        payment.cash_account_id = original.cash_account_id
        from datetime import UTC, datetime
        payment.reversed_at = datetime.now(UTC)
        self.db.commit()
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'reversal_mismatch': 1})

    def test_orphan_payment_movement_is_reported(self):
        _, payment, _ = self.paid_order()
        self.db.delete(payment)
        self.db.commit()
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'orphan_ledger': 1})
