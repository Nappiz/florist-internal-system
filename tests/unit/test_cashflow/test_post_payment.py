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
    def test_payment_helper_posts_once_and_does_not_commit(self):
        account = self.account()
        payment = SimpleNamespace(id=uuid4(), cash_account_id=account['id'], payment_date=self.day, amount=250, reversed_at=None)
        row = post_payment(self.db, self.actor, 'order_payment', payment)
        self.assertEqual(row.direction, 'IN')
        self.assertEqual(post_payment(self.db, self.actor, 'order_payment', payment).id, row.id)
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(CashTransaction)), 1)

