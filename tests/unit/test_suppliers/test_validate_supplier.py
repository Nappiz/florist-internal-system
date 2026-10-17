import unittest
from datetime import UTC, date, datetime
from unittest.mock import patch

from fastapi import HTTPException

from use_cases.suppliers.validate_supplier import validate_supplier


class ClockAfterJakartaMidnight(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 10, 14, 17, 30, tzinfo=UTC).astimezone(tz or UTC)


class ValidateSupplierTests(unittest.TestCase):
    def test_last_checked_date_uses_jakarta_day_after_utc_midnight_boundary(self):
        with patch("use_cases.suppliers.validate_supplier.datetime", ClockAfterJakartaMidnight):
            validate_supplier({"last_checked_at": date(2026, 10, 15)})
            with self.assertRaises(HTTPException) as error:
                validate_supplier({"last_checked_at": date(2026, 10, 16)})
            self.assertEqual(error.exception.status_code, 422)

    def test_required_null_is_rejected_but_nullable_notes_can_be_cleared(self):
        with self.assertRaises(HTTPException):
            validate_supplier({"price": None})
        self.assertEqual(validate_supplier({"notes": None}), {"notes": None})
