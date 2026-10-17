from tests.helpers.auth import AuthEndpointTestCase
from routes.operational_expenses import router
from routes.expense_categories import router as category_router
from models.expense_category_model import ExpenseCategory
from models.operating_expense_model import OperatingExpense
from models.expense_payment_model import ExpensePayment
from models.expense_receipt_model import ExpenseReceipt
from models.cash_account_model import CashAccount
from sqlalchemy.orm import Session
from datetime import date

class OperationalExpenseEndpointTestCase(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
        self.login_as()
        response=self.client.post('/api/v1/expense-categories',json={'name':'Marketing'})
        self.assertEqual(response.status_code,201,response.text)
        self.category=response.json()['id']
