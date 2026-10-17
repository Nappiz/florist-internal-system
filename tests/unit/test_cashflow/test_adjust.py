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
    def test_adjustment_requires_superadmin_and_rejects_inactive_account(self):
        account = self.account()
        data = AdjustmentInput(operation_key=uuid4(), cash_account_id=account['id'], amount=50, direction='OUT', category='owner_withdrawal', reason='Owner withdrawal', transaction_date=self.day)
        staff = SimpleNamespace(user=SimpleNamespace(id=uuid4(), is_superadmin=False, role='staff', is_active=True))
        with self.assertRaises(HTTPException) as caught:
            adjust(self.db, staff, data)
        self.assertEqual(caught.exception.status_code, 403)
        self.db.get(CashAccount, account['id']).is_active = False
        self.db.commit()
        with self.assertRaises(HTTPException):
            adjust(self.db, self.actor, data)

