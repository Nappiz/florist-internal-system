from tests.helpers.auth import AuthEndpointTestCase


class CatalogueEndpointTestCase(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
        self.login_as('staff')

    def material(self,**changes):
        data={'sku':'PC-RED','name':'Pipe cleaner red','base_unit':'pcs'}
        data.update(changes)
        response=self.client.post('/api/v1/materials',json=data)
        self.assertEqual(response.status_code,201,response.text)
        return response.json()

    def supplier(self,**changes):
        data={'name':'Shop','platform':'offline'}
        data.update(changes)
        response=self.client.post('/api/v1/suppliers',json=data)
        self.assertEqual(response.status_code,201,response.text)
        return response.json()

    def listing(self,material,supplier,**changes):
        data={'material_id':material['id'],'supplier_id':supplier['id'],'listing_name':'Pipe cleaner','package_quantity':'100','package_unit':'pcs','quantity_in_base_unit':'100','listed_price':20000}
        data.update(changes)
        response=self.client.post('/api/v1/supplier-materials',json=data)
        self.assertEqual(response.status_code,201,response.text)
        return response.json()
