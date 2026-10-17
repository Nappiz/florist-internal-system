from tests.helpers.auth import AuthEndpointTestCase


class PurchasingTests(AuthEndpointTestCase):
    def test_receiving_weighted_average_and_duplicate_guard(self):
        self.login_as()
        material = self.client.post('/api/v1/materials', json={'sku':'PC-RED','name':'Pipe cleaner red','base_unit':'pcs','minimum_stock':'10'} )
        self.assertEqual(material.status_code,201,material.text)
        material=material.json()
        supplier=self.client.post('/api/v1/suppliers',json={'name':'Shop A','platform':'shopee'}).json()
        listing=self.client.post('/api/v1/supplier-materials',json={'material_id':material['id'],'supplier_id':supplier['id'],'listing_name':'100 pcs','package_quantity':'100','package_unit':'pcs','quantity_in_base_unit':'100','listed_price':20000})
        self.assertEqual(listing.status_code,201,listing.text)
        listing=listing.json()
        self.assertEqual(listing['normalized_unit_price'],'200.00000000')
        purchase=self.client.post('/api/v1/purchases',json={'supplier_id':supplier['id'],'purchase_date':'2026-10-01','shipping_cost':5000,'items':[{'material_id':material['id'],'supplier_listing_id':listing['id'],'quantity':'2'}]})
        self.assertEqual(purchase.status_code,201,purchase.text)
        purchase=purchase.json()
        self.assertEqual(purchase['total_amount'],45000)
        self.assertEqual(self.client.get('/api/v1/inventory/'+material['id']).json()['quantity_on_hand'],'0.000000')
        path='/api/v1/purchases/'+purchase['id']
        self.assertEqual(self.client.post(path+'/order').status_code,200)
        self.assertEqual(self.client.post(path+'/receive').status_code,200)
        self.assertEqual(self.client.post(path+'/receive').status_code,409)
        balance=self.client.get('/api/v1/inventory/'+material['id']).json()
        self.assertEqual(balance['quantity_on_hand'],'200.000000')
        self.assertEqual(balance['average_unit_cost'],'200.00000000')
        self.assertEqual(self.client.patch(path,json={'shipping_cost':0}).status_code,409)
        self.assertEqual(self.client.delete('/api/v1/materials/'+material['id']).status_code,204)
        self.assertEqual(self.client.get('/api/v1/materials/'+material['id']).json()['is_active'],False)

    def test_staff_cannot_adjust_inventory_and_missing_auth(self):
        self.assertEqual(self.client.get('/api/v1/materials').status_code,401)
        self.login_as('staff')
        response=self.client.post('/api/v1/inventory/adjustments',json={'adjustment_key':'00000000-0000-0000-0000-000000000002','material_id':'00000000-0000-0000-0000-000000000001','quantity_delta':'1','unit_cost':'200','reason':'Opening balance'})
        self.assertEqual(response.status_code,403,response.text)
