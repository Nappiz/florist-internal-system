from fastapi import HTTPException

from schemas.flower_schema import FlowerCreate, FlowerUpdate
from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.flowers.create_flower import create_flower
from use_cases.flowers.update_flower import update_flower


class UpdateFlowerTests(CatalogueTestCase):
    def test_activation_requires_composition(self):
        created = create_flower(self.db, self.actor, FlowerCreate(sku="F", name="Tulip", selling_price=1000, is_active=False))
        with self.assertRaises(HTTPException):
            update_flower(self.db, self.actor, created["id"], FlowerUpdate(is_active=True))

