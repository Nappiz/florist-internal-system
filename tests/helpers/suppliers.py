from tests.helpers.auth import AuthEndpointTestCase
from sqlalchemy.orm import Session
from uuid import UUID
from models import User,AuthSession
from schemas.auth_schema import AuthContext
from schemas.supplier_schema import SupplierCreate
from use_cases.suppliers.create_supplier import create_supplier


class SupplierEndpointTestCase(AuthEndpointTestCase):
    def payload(self, **changes):
        values = {
            "material_name": "Pipe Cleaner", "store_name": "Toko A",
            "purchase_url": "https://example.com/product/pipe-cleaner",
            "price": "12000.00", "pack_quantity": "100.000", "unit": "pcs",
        }
        values.update(changes)
        return values

    def create_record(self, **changes):
        # Historical fixture: retired write endpoints cannot create new research.
        user_id=UUID(self.client.get('/auth/me').json()['user']['id'])
        with Session(self.engine) as db:
            actor=AuthContext(db.get(User,user_id),AuthSession(),'fixture')
            return create_supplier(db,actor,SupplierCreate(**self.payload(**changes))).model_dump(mode='json')
