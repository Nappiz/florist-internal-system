from datetime import datetime,timedelta,timezone
from decimal import Decimal
from uuid import uuid4
from tests.helpers.auth import AuthEndpointTestCase


class PurchaseToFulfillmentTests(AuthEndpointTestCase):
    def post(self,path,data=None,status=200):
        response=self.client.post('/api/v1'+path,json=data)
        self.assertEqual(response.status_code,status,response.text)
        return response.json() if status!=204 else None

    def test_research_purchase_receive_bom_order_production_payment_reporting(self):
        self.login_as('staff')
        today=datetime.now(timezone(timedelta(hours=7))).date().isoformat()
        red=self.post('/materials',{'sku':'E2E-RED','name':'Red pipe cleaner','minimum_stock':'190'},201)
        wrap=self.post('/materials',{'sku':'E2E-WRAP','name':'Wrapping paper','minimum_stock':'1'},201)
        shop=self.post('/suppliers',{'name':'E2E Shop','platform':'shopee'},201)
        listing=self.post('/supplier-materials',{'material_id':red['id'],'supplier_id':shop['id'],'listing_name':'Red 100 pcs','package_quantity':'100','package_unit':'pcs','quantity_in_base_unit':'100','listed_price':20000},201)
        purchase=self.post('/purchases',{'supplier_id':shop['id'],'purchase_date':today,'shipping_cost':5000,'discount_amount':1000,'items':[{'material_id':red['id'],'supplier_listing_id':listing['id'],'quantity':'2'},{'material_id':wrap['id'],'quantity':'10','unit_price':1000}]},201)
        self.assertEqual(purchase['total_amount'],54000)
        self.assertEqual(Decimal(self.client.get('/api/v1/inventory/'+red['id']).json()['quantity_on_hand']),0)
        self.post('/purchases/'+purchase['id']+'/order')
        self.post('/purchases/'+purchase['id']+'/receive')
        self.post('/purchases/'+purchase['id']+'/payments',{'cash_account_id':self.cash_account_id,'payment_key':str(uuid4()),'payment_date':today,'amount':54000},201)
        flower=self.post('/flowers',{'sku':'E2E-TULIP','name':'Red Tulip','selling_price':3000,'estimated_labor_cost':500,'bom':{'materials':[{'material_id':red['id'],'quantity_required':'3','unit':'pcs'}]}},201)
        self.assertEqual(Decimal(flower['estimated_hpp']),1100)
        product=self.post('/products',{'sku':'E2E-BOUQUET','name':'Bouquet','selling_price':15000,'assembly_labor_cost':1000,'bom':{'flowers':[{'flower_id':flower['id'],'quantity_required':'3'}],'materials':[{'material_id':wrap['id'],'quantity_required':'1','unit':'pcs'}]}},201)
        self.assertEqual(Decimal(product['estimated_hpp']),5300)
        order=self.post('/orders',{'customer_name':'Customer','customer_phone':'+62 812-3456-7890','sales_channel':'whatsapp','items':[{'product_id':product['id'],'quantity':1},{'flower_id':flower['id'],'quantity':2}]},201)
        self.assertEqual(order['total_amount'],21000)
        path='/orders/'+order['id']
        self.post(path+'/confirm')
        self.assertEqual(Decimal(self.client.get('/api/v1/inventory/'+red['id']).json()['quantity_on_hand']),200)
        self.post(path+'/payments',{'cash_account_id':self.cash_account_id,'payment_key':str(uuid4()),'amount':10000})
        self.post(path+'/start-production')
        ready=self.post(path+'/complete-production')
        self.assertEqual(Decimal(ready['production']['actual_material_cost']),4000)
        self.assertEqual(Decimal(ready['production']['labor_cost_snapshot']),3500)
        self.assertEqual(Decimal(ready['production']['total_production_cost']),7500)
        self.post(path+'/payments',{'cash_account_id':self.cash_account_id,'payment_key':str(uuid4()),'amount':11000})
        completed=self.post(path+'/complete')
        self.assertEqual(completed['payment_status'],'paid')
        self.assertTrue(completed['history'])
        self.assertEqual(Decimal(self.client.get('/api/v1/inventory/'+red['id']).json()['quantity_on_hand']),185)
        self.assertEqual(Decimal(self.client.get('/api/v1/inventory/'+wrap['id']).json()['quantity_on_hand']),9)
        self.assertEqual(self.client.post('/api/v1'+path+'/complete-production').status_code,409)
        period='?date_from='+today+'&date_to='+today
        sales=self.client.get('/api/v1/reports/sales'+period).json()
        profit=self.client.get('/api/v1/reports/profitability'+period).json()
        self.assertEqual(sales['completed_sales_total'],21000)
        self.assertEqual(sales['collections_total'],21000)
        self.assertEqual(Decimal(profit['gross_margin']),13500)
        inventory=self.client.get('/api/v1/reports/inventory'+period).json()
        self.assertEqual(Decimal(inventory['inventory_value']),46000)
        self.assertEqual(inventory['low_stock_count'],1)
