import unittest
from decimal import Decimal
from types import SimpleNamespace

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from models import Base, User
from models.material_model import Material
from models.supplier_store_model import SupplierStore
from models.supplier_material_model import SupplierMaterial
from models.inventory_balance_model import InventoryBalance
from models.flower_model import Flower
from models.flower_material_model import FlowerMaterial
from models.product_model import Product
from models.product_flower_model import ProductFlower
from models.product_material_model import ProductMaterial
from use_cases.catalogue.costing import flower_recipe, material_cost, product_recipe


class CatalogueTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        event.listen(self.engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(username="catalogue", password_hash="unused", is_superadmin=True)
        self.material = Material(sku="MAT-1", name="Pipe cleaner", base_unit="pcs", minimum_stock=0, is_active=True)
        self.db.add_all([self.user, self.material])
        self.db.commit()
        self.actor = SimpleNamespace(user=self.user)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def flower(self, quantity="2", labor=100):
        flower = Flower(sku="FLW-1", name="Tulip", selling_price=1000, estimated_labor_cost=labor, is_active=True)
        self.db.add(flower)
        self.db.flush()
        self.db.add(FlowerMaterial(flower_id=flower.id, material_id=self.material.id, quantity_required=Decimal(quantity), unit="pcs"))
        self.db.commit()
        return flower

