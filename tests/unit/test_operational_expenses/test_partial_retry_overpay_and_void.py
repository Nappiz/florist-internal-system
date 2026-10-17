from tests.helpers.operational_expenses import *

class ExpenseTest(OperationalExpenseTestCase):
    def test_partial_retry_overpay_and_void(self):
        row=self.create(); post_expense(self.db,self.admin,row['id'])
        data=ExpensePaymentCreate(payment_key=uuid4(),cash_account_id=uuid4(),payment_date=date.today(),amount=40,method='cash')
        with patch('use_cases.cashflow.post_payment.post_payment') as cash:
            result=add_payment(self.db,self.admin,row['id'],data)
            self.assertEqual(result['payment_status'],'partial')
            add_payment(self.db,self.admin,row['id'],data)
            self.assertEqual(cash.call_count,1)
        with self.assertRaises(HTTPException): add_payment(self.db,self.admin,row['id'],data.model_copy(update={'payment_key':uuid4(),'amount':70}))
        with self.assertRaises(HTTPException): void_expense(self.db,self.admin,row['id'],'mistake')
