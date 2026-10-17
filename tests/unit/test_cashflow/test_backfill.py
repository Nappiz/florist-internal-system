from uuid import uuid4
from fastapi import HTTPException
from models import Order, OrderPayment
from schemas.cashflow_schema import BackfillInput, HistoricalMapping, CashflowQuery
from tests.unit.test_cashflow.base import CashTestCase
from use_cases.cashflow.backfill import backfill
from use_cases.cashflow.reconcile import reconcile
from use_cases.cashflow.summary import summary


class BackfillTests(CashTestCase):
    def historical(self):
        order = Order(order_number='HIST-' + uuid4().hex, customer_name='Historical', order_date=self.day, subtotal=500, total_amount=500, payment_status='paid')
        self.db.add(order)
        self.db.flush()
        payment = OrderPayment(id=uuid4(), order_id=order.id, payment_key=uuid4(), payment_date=self.day, amount=500)
        self.db.add(payment)
        self.db.commit()
        return payment

    def test_mapping_is_explicit_idempotent_and_reconciles_history(self):
        payment = self.historical()
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'unmapped_payment': 1})
        account = self.account(amount=0, mode='backfill')
        data = BackfillInput(operation_key=uuid4(), reason='Validated bank statement', mappings=[HistoricalMapping(source_type='order_payment', payment_id=payment.id, cash_account_id=account['id'])])
        result = backfill(self.db, self.actor, data)
        retry = backfill(self.db, self.actor, data)
        self.assertEqual(result, retry)
        self.assertEqual(payment.cash_account_id, account['id'])
        self.assertTrue(reconcile(self.db, self.actor)['is_reconciled'])
        self.assertEqual(summary(self.db, self.actor, CashflowQuery())['closing_balance'], 500)

    def test_opening_strategy_rejects_backfill_without_partial_mapping(self):
        payment = self.historical()
        account = self.account()
        data = BackfillInput(operation_key=uuid4(), reason='Attempt duplicate balance', mappings=[HistoricalMapping(source_type='order_payment', payment_id=payment.id, cash_account_id=account['id'])])
        with self.assertRaises(HTTPException) as caught:
            backfill(self.db, self.actor, data)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIsNone(payment.cash_account_id)
        self.assertEqual(summary(self.db, self.actor, CashflowQuery())['closing_balance'], 1000)

    def test_late_mapping_error_rolls_back_earlier_payment_and_movement(self):
        from uuid import UUID
        first, second = self.historical(), self.historical()
        first.id, second.id = UUID(int=1), UUID(int=2)
        second.payment_date = self.day.replace(year=2025)
        self.db.commit()
        account = self.account(amount=0, mode='backfill')
        key = uuid4()
        data = BackfillInput(operation_key=key, reason='Batch validated mappings', mappings=[HistoricalMapping(source_type='order_payment', payment_id=row.id, cash_account_id=account['id']) for row in (first, second)])
        with self.assertRaises(HTTPException) as caught:
            backfill(self.db, self.actor, data)
        self.assertEqual(caught.exception.status_code, 422)
        self.assertIsNone(first.cash_account_id)
        self.assertIsNone(second.cash_account_id)
        self.assertEqual(summary(self.db, self.actor, CashflowQuery())['closing_balance'], 0)
        self.assertEqual(reconcile(self.db, self.actor)['issue_counts'], {'unmapped_payment': 2})
