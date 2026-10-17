from tests.helpers.operational_expenses import *
from schemas.expense_category_schema import CategoryCreate,CategoryUpdate
from use_cases.expense_categories.create_category import create_category
from use_cases.expense_categories.archive_category import archive_category

class CategoryTest(OperationalExpenseTestCase):
    def test_permissions_archive_and_inventory_category(self):
        with self.assertRaises(HTTPException): create_category(self.db,self.staff,CategoryCreate(name='Equipment',classification='equipment'))
        with self.assertRaises(HTTPException): create_category(self.db,self.admin,CategoryCreate(name='Raw materials'))
        row=create_category(self.db,self.admin,CategoryCreate(name='Equipment',classification='equipment'))
        archive_category(self.db,self.admin,row.id)
        with self.assertRaises(HTTPException): create_expense(self.db,self.staff,ExpenseCreate(category_id=row.id,title='Drill',expense_date=date.today(),amount=100))
