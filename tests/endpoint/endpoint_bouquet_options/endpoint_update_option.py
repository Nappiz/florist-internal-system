from tests.endpoint.endpoint_custom_bouquets.support import BouquetEndpointCase

class UpdateOptionTests(BouquetEndpointCase):
    def test_admin_can_patch_only_option_price(self):
        self.login_as("superadmin")
        response=self.client.post("/bouquet-test/bouquet-options",json={"name":"Card","option_group":"greeting_card","selling_price":100,"requires_materials":False,"image_url":"https://example.com/card.png"})
        self.assertEqual(response.status_code,201,response.text)
        identity=response.json()["id"]
        response=self.client.patch(f"/bouquet-test/bouquet-options/{identity}",json={"selling_price":200})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["name"],"Card")
        self.assertEqual(response.json()["selling_price"],200)
