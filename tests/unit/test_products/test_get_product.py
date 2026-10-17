from sqlalchemy import event
from sqlalchemy.dialects import postgresql

from schemas.product_schema import ProductCreate
from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.products.create_product import create_product
from use_cases.products.get_product import get_product


class ProductReadLockTests(CatalogueTestCase):
    def test_reading_availability_does_not_acquire_master_locks(self):
        flower = self.flower()
        product = create_product(self.db, self.actor, ProductCreate(sku="P", name="Bouquet", selling_price=5000, bom={"flowers": [{"flower_id": flower.id, "quantity_required": 1}]}))
        queries = []

        def capture(connection, statement, multiparams, params, execution_options):
            queries.append(str(statement.compile(dialect=postgresql.dialect())))

        event.listen(self.engine, "before_execute", capture)
        self.assertEqual(get_product(self.db, product["id"])["available_quantity"], 0)
        self.assertFalse(any("FOR UPDATE" in query for query in queries))

