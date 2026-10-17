from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select

from schemas.flower_schema import FlowerBOM
from tests.unit.test_catalogue.base import CatalogueTestCase, FlowerMaterial
from use_cases.flowers.replace_bom import replace_bom


class ReplaceFlowerBOMTests(CatalogueTestCase):
    def test_replace_bom_merges_duplicates_and_validates_unit(self):
        flower = self.flower()
        bom = FlowerBOM(materials=[{"material_id": self.material.id, "quantity_required": "1.2", "unit": "pcs"}, {"material_id": self.material.id, "quantity_required": "0.3", "unit": "pcs"}])
        replace_bom(self.db, self.actor, flower.id, bom)
        rows = list(self.db.scalars(select(FlowerMaterial).where(FlowerMaterial.flower_id == flower.id)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].quantity_required, Decimal("1.5"))
        with self.assertRaises(HTTPException):
            replace_bom(self.db, self.actor, flower.id, FlowerBOM(materials=[{"material_id": self.material.id, "quantity_required": 1, "unit": "meter"}]))
        self.assertEqual(self.db.scalars(select(FlowerMaterial)).one().quantity_required, Decimal("1.5"))

