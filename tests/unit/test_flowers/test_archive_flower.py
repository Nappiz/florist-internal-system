from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.flowers.archive_flower import archive_flower


class ArchiveFlowerTests(CatalogueTestCase):
    def test_archive_preserves_record(self):
        flower = self.flower()
        archive_flower(self.db, self.actor, flower.id)
        self.assertFalse(flower.is_active)
