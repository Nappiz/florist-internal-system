from uuid import uuid4
from tests.helpers.catalogue import CatalogueEndpointTestCase


class PurchaseUpdateTests(CatalogueEndpointTestCase):
    def purchase(self):
        material=self.material()
        store=self.supplier()
        listing=self.listing(material,store)
        response=self.client.post('/api/v1/purchases',json={'supplier_id':store['id'],'purchase_date':'2026-10-01','items':[{'material_id':material['id'],'supplier_listing_id':listing['id'],'quantity':'1'}]})
        self.assertEqual(response.status_code,201,response.text)
        return response.json(),listing

    def test_draft_updates_totals_atomically_and_does_not_flush_partial_header(self):
        purchase,listing=self.purchase()
        path='/api/v1/purchases/'+purchase['id']
        response=self.client.patch(path,json={'shipping_cost':5000,'discount_amount':2000})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['total_amount'],23000)
        changed=self.client.patch('/api/v1/supplier-materials/'+listing['id'],json={'listed_price':30000})
        self.assertEqual(changed.status_code,200,changed.text)
        self.assertEqual(self.client.get(path).json()['items'][0]['unit_price'],20000)
        self.assertEqual(self.client.get('/api/v1/purchases?min_total=23000&max_total=23000').json()['total'],1)
        self.assertEqual(self.client.get('/api/v1/purchases?min_total=100&max_total=1').status_code,422)
        free=self.client.patch(path,json={'discount_amount':25000})
        self.assertEqual(free.status_code,200,free.text)
        self.assertEqual(free.json()['total_amount'],0)
        self.assertEqual(free.json()['payment_status'],'paid')

    def test_payment_retries_overpayments_and_invalid_updates_preserve_history(self):
        purchase,_=self.purchase()
        path='/api/v1/purchases/'+purchase['id']
        data={'cash_account_id':self.cash_account_id,'payment_key':str(uuid4()),'payment_date':'2026-10-01','amount':10000}
        first=self.client.post(path+'/payments',json=data)
        self.assertEqual(first.status_code,201,first.text)
        self.assertEqual(first.json()['payment_status'],'partial')
        self.assertEqual(self.client.post(path+'/payments',json=data).status_code,201)
        self.assertEqual(len(self.client.get(path).json()['payments']),1)
        self.assertEqual(self.client.post(path+'/payments',json={**data,'amount':9000}).status_code,409)
        self.assertEqual(self.client.post(path+'/payments',json={**data,'payment_key':str(uuid4()),'amount':10001}).status_code,409)
        self.assertEqual(self.client.patch(path,json={'items':[]}).status_code,422)
        self.assertEqual(self.client.patch(path,json={'discount_amount':11000}).status_code,409)
        self.assertEqual(self.client.get(path).json()['total_amount'],20000)
        self.assertEqual(self.client.post(path+'/payments',json={**data,'payment_key':str(uuid4())}).json()['payment_status'],'paid')
