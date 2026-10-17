import unittest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from models.supplier_model import Supplier
from use_cases.suppliers.supplier_response import supplier_response


class SupplierResponseTests(unittest.TestCase):
    def make_record(self, **changes):
        values = dict(
            id=uuid4(), material_name="Pipe cleaner", store_name="Toko A",
            purchase_url="https://example.com/material", price=Decimal("10000.00"),
            pack_quantity=Decimal("3.000"), unit="pcs", last_checked_at=datetime.now(UTC).date(),
            created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
        )
        values.update(changes)
        return Supplier(**values)

    def test_decimal_unit_price_rounds_half_up_and_unknown_shipping_stays_unknown(self):
        response = supplier_response(self.make_record())
        self.assertEqual(response.unit_price, Decimal("3333.3333"))
        self.assertIsNone(response.landed_unit_price)
        rounded = supplier_response(self.make_record(price=Decimal("1.00"), pack_quantity=Decimal("32")))
        self.assertEqual(rounded.unit_price, Decimal("0.0313"))

    def test_known_shipping_is_included_and_zero_shipping_is_not_unknown(self):
        response = supplier_response(self.make_record(estimated_shipping_cost=Decimal("5000.00")))
        self.assertEqual(response.landed_unit_price, Decimal("5000.0000"))
        free = supplier_response(self.make_record(estimated_shipping_cost=Decimal("0.00")))
        self.assertEqual(free.landed_unit_price, Decimal("3333.3333"))
