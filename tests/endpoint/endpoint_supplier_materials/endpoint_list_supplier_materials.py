from uuid import uuid4
from tests.helpers.catalogue import CatalogueEndpointTestCase


class NormalizedCatalogueTests(CatalogueEndpointTestCase):
    def test_multiple_stores_comparison_literal_filters_and_partial_updates(self):
        material=self.material()
        first=self.supplier(name='Store A',platform='shopee')
        second=self.supplier(name='Store B',platform='tokopedia')
        listing=self.listing(material,first)
        cheaper=self.listing(material,second,listed_price=8500,package_quantity='50',quantity_in_base_unit='50')
        page=self.client.get('/api/v1/supplier-materials',params={'material_id':material['id'],'sort':'unit_price_asc','min_price':8000,'max_price':21000}).json()
        self.assertEqual([row['id'] for row in page['items']],[cheaper['id'],listing['id']])
        self.assertEqual(page['items'][0]['normalized_unit_price'],'170.00000000')
        self.assertEqual(self.client.get('/api/v1/supplier-materials',params={'q':"' OR 1=1 --"}).json()['total'],0)
        changed=self.client.patch('/api/v1/supplier-materials/'+listing['id'],json={'listed_price':25000,'notes':'Updated reference'})
        self.assertEqual(changed.status_code,200,changed.text)
        self.assertEqual(changed.json()['normalized_unit_price'],'250.00000000')
        self.assertEqual(self.client.patch('/api/v1/materials/'+material['id'],json={'base_unit':'meter'}).status_code,409)
        self.assertEqual(self.client.get('/api/v1/supplier-materials?min_price=10&max_price=1').status_code,422)

    def test_archive_keeps_references_and_blocks_new_transactions(self):
        material=self.material()
        supplier=self.supplier()
        listing=self.listing(material,supplier)
        self.assertEqual(self.client.delete('/api/v1/supplier-materials/'+listing['id']).status_code,204)
        response=self.client.post('/api/v1/purchases',json={'supplier_id':supplier['id'],'purchase_date':'2026-10-01','items':[{'material_id':material['id'],'supplier_listing_id':listing['id'],'quantity':'1'}]})
        self.assertEqual(response.status_code,409,response.text)
        self.assertEqual(self.client.get('/api/v1/supplier-materials/'+listing['id']).json()['is_active'],False)
        self.assertEqual(self.client.delete('/api/v1/suppliers/'+supplier['id']).status_code,204)
        self.assertEqual(self.client.patch('/api/v1/suppliers/'+supplier['id'],json={'is_active':True}).status_code,200)

    def test_boundary_validation_csrf_unknown_fields_and_no_upload(self):
        for data in ({'sku':'BAD','name':' ','base_unit':'pcs'}, {'sku':'BAD','name':'Bad','minimum_stock':'NaN'},{'sku':'BAD','name':'Bad','created_by':self.admin_id},{'sku':'BAD','name':'Bad','image_url':'https://a.example/'+'a'*2040}):
            self.assertEqual(self.client.post('/api/v1/materials',json=data).status_code,422)
        material=self.material()
        supplier=self.supplier()
        response=self.client.post('/api/v1/supplier-materials',json={'material_id':material['id'],'supplier_id':supplier['id'],'listing_name':'Bad cost','package_quantity':'1','package_unit':'pack','quantity_in_base_unit':'0.000001','listed_price':999999999999999})
        self.assertEqual(response.status_code,422,response.text)
        self.assertEqual(self.client.get('/api/v1/inventory/movements?date_from=2026-10-01T00:00:00&date_to=2026-10-02T00:00:00Z').status_code,422)
        self.client.headers.pop('X-CSRF-Token')
        self.assertEqual(self.client.patch('/api/v1/materials/'+material['id'],json={'name':'new'}).status_code,403)
        self.assertEqual(self.client.post('/api/v1/uploads',files={'image':('bad.svg',b'<svg onload="alert(1)"/>','image/svg+xml')}).status_code,404)
