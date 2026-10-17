import unittest
from datetime import date
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User
from models.expense_category_model import ExpenseCategory
from models.operating_expense_model import OperatingExpense
from models.expense_payment_model import ExpensePayment
from models.expense_receipt_model import ExpenseReceipt
from schemas.operational_expense_schema import ExpenseCreate, ExpenseUpdate, ExpensePaymentCreate, ExpenseListQuery
from use_cases.operational_expenses.create_expense import create_expense
from use_cases.operational_expenses.update_expense import update_expense
from use_cases.operational_expenses.post_expense import post_expense
from use_cases.operational_expenses.get_expense import get_expense
from use_cases.operational_expenses.add_payment import add_payment
from use_cases.operational_expenses.void_expense import void_expense
from use_cases.operational_expenses.expense_summary import expense_summary

class OperationalExpenseTestCase(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://')
        Base.metadata.create_all(self.engine)
        self.db=Session(self.engine)
        admin=User(username='admin',password_hash='x',is_superadmin=True)
        staff=User(username='staff',password_hash='x')
        other=User(username='other',password_hash='x')
        category=ExpenseCategory(name='Marketing',classification='operational')
        self.db.add_all([admin,staff,other,category]); self.db.commit()
        self.admin=SimpleNamespace(user=admin); self.staff=SimpleNamespace(user=staff); self.other=SimpleNamespace(user=other); self.category=category
    def tearDown(self):
        self.db.close(); self.engine.dispose()
    def create(self):
        return create_expense(self.db,self.staff,ExpenseCreate(category_id=self.category.id,title='Ads',expense_date=date.today(),amount=100))
