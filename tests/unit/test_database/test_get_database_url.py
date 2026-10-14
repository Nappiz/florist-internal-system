import unittest
from unittest.mock import patch

from configs.database import get_database_url
from configs.settings import Settings


class GetDatabaseUrlTests(unittest.TestCase):
    def test_supabase_postgres_url_uses_psycopg_and_preserves_encoded_password(self):
        settings = Settings(
            _env_file=None,
            database_url="postgres://postgres:p%40ss%25word@localhost:5432/postgres",
        )
        with patch("configs.database.get_settings", return_value=settings):
            url = get_database_url()
        self.assertEqual(url.drivername, "postgresql+psycopg")
        self.assertEqual(url.password, "p@ss%word")

    def test_missing_database_url_explains_required_configuration(self):
        with patch(
            "configs.database.get_settings",
            return_value=Settings(_env_file=None, database_url=None),
        ):
            with self.assertRaisesRegex(ValueError, "DATABASE_URL"):
                get_database_url()

    def test_invalid_url_does_not_expose_credential_in_error(self):
        for value in (
            "https://example.com/secret-credential",
            "postgresql://postgres:secret-credential@localhost:invalid/postgres",
        ):
            with self.subTest(value=value):
                with patch(
                    "configs.database.get_settings",
                    return_value=Settings(_env_file=None, database_url=value),
                ):
                    with self.assertRaises(ValueError) as error:
                        get_database_url()
                self.assertNotIn("secret-credential", str(error.exception))


if __name__ == "__main__":
    unittest.main()
