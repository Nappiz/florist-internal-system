from tests.endpoint.endpoint_custom_bouquets.support import BouquetEndpointCase

class UpdateSettingsTests(BouquetEndpointCase):
    def test_pricing_settings_and_option_master_require_admin(self):
        settings={"min_stems":2,"max_stems":10,"minimum_price":50000,"assembly_fee":1000,"assembly_labor_cost":"30"}
        option={"name":"Ribbon","option_group":"ribbon","selling_price":500,"materials":[{"material_id":self.material_id,"quantity_required":"1","unit":"pcs"}]}
        self.assertEqual(self.client.put("/bouquet-test/bouquet-settings",json=settings).status_code,403)
        self.assertEqual(self.client.post("/bouquet-test/bouquet-options",json=option).status_code,403)
        self.login_as("superadmin")
        response=self.client.put("/bouquet-test/bouquet-settings",json=settings)
        self.assertEqual(response.status_code,200,response.text)
        response=self.client.post("/bouquet-test/bouquet-options",json=option)
        self.assertEqual(response.status_code,201,response.text)
        identity=response.json()["id"]
        self.assertEqual(response.json()["materials"][0]["material_id"],self.material_id)
        self.login_as("staff")
        response=self.client.post("/bouquet-test/custom-bouquets/estimate",json={**self.payload,"options":[{"bouquet_option_id":identity,"quantity":1}]})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["proposed_price"],50000)
        self.assertEqual(self.client.get("/bouquet-test/bouquet-options").json()["total"],1)
