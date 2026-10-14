import unittest

from fastapi import HTTPException

from use_cases.users.validate_password import validate_password


class ValidatePasswordTests(unittest.TestCase):
    def test_accepts_password_meeting_all_requirements(self):
        validate_password("Example10@")

    def test_rejects_each_missing_requirement(self):
        for password in ("Ab1@", "lowercase1@", "UPPERCASE1@", "NoSpecial10", "With space10"):
            with self.subTest(password=password):
                with self.assertRaises(HTTPException) as error:
                    validate_password(password)
                self.assertEqual(error.exception.status_code, 422)
                self.assertNotIn(password, error.exception.detail)
