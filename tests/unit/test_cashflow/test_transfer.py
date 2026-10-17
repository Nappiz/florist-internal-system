import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from models import Base, User
from models.cash_account_model import CashAccount
from models.cash_operation_model import CashOperation
from models.cash_transaction_model import CashTransaction
from schemas.cash_account_schema import CashAccountCreate
from schemas.cashflow_schema import AdjustmentInput, TransferInput, CashflowQuery, ReverseInput
from use_cases.cash_accounts.create_account import create_account
from use_cases.cashflow.adjust import adjust
from use_cases.cashflow.transfer import transfer
from use_cases.cashflow.post_payment import post_payment
from use_cases.cashflow.summary import summary
from use_cases.cashflow.history import history
from use_cases.cashflow.reverse_payment import reverse_payment


from tests.unit.test_cashflow.base import CashTestCase


class CashTests(CashTestCase):
    def test_second_transfer_insert_failure_rolls_back_both_sides_and_operation(self):
        from sqlalchemy import text
        first, second = self.account('Cash'), self.account('Bank', 0)
        key = uuid4()
        self.db.execute(text("CREATE TRIGGER reject_transfer_credit BEFORE INSERT ON cash_transactions WHEN NEW.source_type = 'transfer' AND NEW.direction = 'IN' BEGIN SELECT RAISE(ABORT, 'simulated posting failure'); END"))
        self.db.commit()
        data = TransferInput(operation_key=key, from_account_id=first['id'], to_account_id=second['id'], amount=300, transaction_date=self.day, reason='Atomic transfer proof')
        with self.assertRaises(HTTPException) as caught:
            transfer(self.db, self.actor, data)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIsNone(self.db.get(CashOperation, key))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(CashTransaction)), 1)
        self.assertEqual(summary(self.db, self.actor, CashflowQuery())['closing_balance'], 1000)

    def test_transfer_preserves_aggregate_and_account_running_balance(self):
        first, second = self.account('Cash'), self.account('Bank', 0)
        data = TransferInput(operation_key=uuid4(), from_account_id=first['id'], to_account_id=second['id'], amount=300, transaction_date=self.day + timedelta(days=1), reason='Deposit')
        transfer(self.db, self.actor, data)
        transfer(self.db, self.actor, data)
        all_accounts = summary(self.db, self.actor, CashflowQuery(date_from=data.transaction_date, date_to=data.transaction_date))
        self.assertEqual((all_accounts['opening_balance'], all_accounts['cash_in'], all_accounts['cash_out'], all_accounts['closing_balance']), (1000, 0, 0, 1000))
        one = summary(self.db, self.actor, CashflowQuery(cash_account_id=first['id'], date_from=data.transaction_date, date_to=data.transaction_date))
        self.assertEqual(one['closing_balance'], 700)
        rows = history(self.db, self.actor, CashflowQuery(cash_account_id=first['id'], date_from=data.transaction_date, limit=1))
        self.assertEqual(rows['items'][0]['running_balance'], 700)

