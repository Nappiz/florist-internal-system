from tests.helpers.suppliers import SupplierEndpointTestCase
from sqlalchemy.orm import Session
from uuid import UUID
from models import User,AuthSession
from schemas.auth_schema import AuthContext
from schemas.expense_schema import ExpenseCreate
from use_cases.expenses.create_expense import create_expense


class ExpenseEndpointTestCase(SupplierEndpointTestCase):
    def purchase(self, source_id, **changes):
        values = {"supplier_id": source_id, "pack_count": 2}
        values.update(changes)
        return values

    def create_expense(self, supplier_id, **changes):
        user_id=UUID(self.client.get('/auth/me').json()['user']['id'])
        with Session(self.engine) as db:
            actor=AuthContext(db.get(User,user_id),AuthSession(),'fixture')
            return create_expense(db,actor,ExpenseCreate(**self.purchase(supplier_id,**changes))).model_dump(mode='json')
