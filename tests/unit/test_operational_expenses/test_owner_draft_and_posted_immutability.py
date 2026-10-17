from tests.helpers.operational_expenses import *

class ExpenseTest(OperationalExpenseTestCase):
    def test_owner_draft_and_posted_immutability(self):
        row=self.create()
        with self.assertRaises(HTTPException): get_expense(self.db,self.other,row['id'])
        with self.assertRaises(HTTPException): post_expense(self.db,self.staff,row['id'])
        post_expense(self.db,self.admin,row['id'])
        with self.assertRaises(HTTPException): update_expense(self.db,self.admin,row['id'],ExpenseUpdate(amount=90))
        self.assertEqual(self.db.query(ExpensePayment).count(),0)
