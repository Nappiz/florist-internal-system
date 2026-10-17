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


class CashTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
        event.listen(self.engine, 'connect', lambda connection, _: connection.execute('PRAGMA foreign_keys=ON'))
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(username='cashowner', password_hash='unused', is_superadmin=True)
        self.db.add(self.user)
        self.db.commit()
        self.actor = SimpleNamespace(user=self.user)
        self.day = date(2026, 1, 1)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def account(self, name='Bank', amount=1000, mode='opening'):
        return create_account(self.db, self.actor, CashAccountCreate(operation_key=uuid4(), name=name, account_type='bank', opening_date=self.day, opening_balance=amount, history_mode=mode, reason='Verified actual opening'))


