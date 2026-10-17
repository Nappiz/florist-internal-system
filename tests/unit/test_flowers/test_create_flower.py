from fastapi import HTTPException

from schemas.flower_schema import FlowerCreate
from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.flowers.create_flower import create_flower


class CreateFlowerTests(CatalogueTestCase):
    def test_active_create_requires_recipe(self):
        with self.assertRaises(HTTPException) as caught:
            create_flower(self.db, self.actor, FlowerCreate(sku="F", name="Tulip", selling_price=1000))
        self.assertEqual(caught.exception.status_code, 422)

