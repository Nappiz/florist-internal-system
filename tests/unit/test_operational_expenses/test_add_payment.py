from tests.helpers.operational_expenses import *
from models.cash_account_model import CashAccount
from models.cash_transaction_model import CashTransaction
from schemas.cashflow_schema import ReverseInput
from use_cases.cashflow.reverse_payment import reverse_payment
from crud.cashflow_crud import balance

class PaymentTest(OperationalExpenseTestCase):
    def test_actual_ledger_reversal_and_atomic_failure(self):
        account=CashAccount(name='Wallet',account_type='cash',opening_date=date.today(),history_mode='backfill')
        self.db.add(account); self.db.commit()
        row=self.create(); post_expense(self.db,self.admin,row['id'])
        data=ExpensePaymentCreate(payment_key=uuid4(),cash_account_id=account.id,payment_date=date.today(),amount=40,method='cash')
        add_payment(self.db,self.admin,row['id'],data)
        self.assertEqual(balance(self.db,account.id),-40)
        movement=self.db.query(CashTransaction).filter_by(source_type='expense_payment').one()
        reverse_payment(self.db,self.admin,movement.id,ReverseInput(operation_key=uuid4(),reason='wrong amount',transaction_date=date.today()))
        self.assertEqual(balance(self.db,account.id),0)
        self.assertEqual(get_expense(self.db,self.admin,row['id'])['payment_status'],'unpaid')
        account.is_active=False; self.db.commit()
        with self.assertRaises(HTTPException): add_payment(self.db,self.admin,row['id'],data.model_copy(update={'payment_key':uuid4(),'amount':60}))
        self.assertEqual(self.db.query(ExpensePayment).count(),1)
        self.assertEqual(self.db.query(CashTransaction).count(),2)
        result=void_expense(self.db,self.admin,row['id'],'fully reversed')
        self.assertEqual(result['status'],'void')
