from uuid import uuid4

from tests.helpers.suppliers import SupplierEndpointTestCase


class GetSupplierEndpointTests(SupplierEndpointTestCase):
    def test_requires_login_and_returns_existing_or_404(self):
        self.assertEqual(self.client.get(f"/suppliers/{uuid4()}").status_code, 401)
        self.login_as("staff")
        record = self.create_record()
        self.assertEqual(self.client.get("/suppliers/" + record["id"]).status_code, 200)
        self.assertEqual(self.client.get(f"/suppliers/{uuid4()}").status_code, 404)
