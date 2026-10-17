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
    def test_opening_is_audited_and_idempotent(self):
        data = CashAccountCreate(operation_key=uuid4(), name='Bank', account_type='bank', opening_date=self.day, opening_balance=1000, reason='Bank statement')
        account = create_account(self.db, self.actor, data)
        retry = create_account(self.db, self.actor, data)
        self.assertEqual(account['id'], retry['id'])
        self.assertEqual(self.db.scalar(select(func.count()).select_from(CashAccount)), 1)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(CashTransaction)), 1)
        result = summary(self.db, self.actor, CashflowQuery(date_from=self.day, date_to=self.day))
        self.assertEqual(result['closing_balance'], 1000)
        with self.assertRaises(HTTPException) as caught:
            create_account(self.db, self.actor, data.model_copy(update={'opening_balance': 1200}))
        self.assertEqual(caught.exception.status_code, 409)

    def test_backfill_mode_cannot_have_opening_money(self):
        with self.assertRaises(HTTPException):
            self.account(amount=1000, mode='backfill')

