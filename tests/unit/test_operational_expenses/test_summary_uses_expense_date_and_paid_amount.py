from tests.helpers.operational_expenses import *

class ExpenseTest(OperationalExpenseTestCase):
    def test_summary_uses_expense_date_and_paid_amount(self):
        row=self.create(); post_expense(self.db,self.admin,row['id'])
        summary=expense_summary(self.db,self.admin,ExpenseListQuery())
        self.assertEqual(summary['total_posted_expenses'],100)
        self.assertEqual(summary['total_unpaid_expenses'],100)
        self.assertEqual(summary['total_paid_expenses'],0)
        with self.assertRaises(HTTPException): expense_summary(self.db,self.staff,ExpenseListQuery())
