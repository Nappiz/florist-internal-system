from tests.helpers.operational_expense_endpoint import OperationalExpenseEndpointTestCase
from tempfile import TemporaryDirectory
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
from datetime import date

class ReceiptEndpointTest(OperationalExpenseEndpointTestCase):
    def test_raw_upload_download_and_type_validation(self):
        self.login_as('staff')
        created=self.client.post('/api/v1/expenses',json={'category_id':self.category,'title':'Receipt','expense_date':date.today().isoformat(),'amount':100}).json()
        url=f"/api/v1/expenses/{created['id']}/receipts"
        with TemporaryDirectory() as directory, patch('services.expense_receipt_storage.get_settings',return_value=SimpleNamespace(private_receipt_dir=Path(directory))):
            invalid=self.client.post(url,content=b'<script>',headers={'Content-Type':'image/png'})
            self.assertEqual(invalid.status_code,415,invalid.text)
            content=b'%PDF-1.4\n'+b'x'*20000
            upload=self.client.post(url,content=content,headers={'Content-Type':'application/pdf'})
            self.assertEqual(upload.status_code,201,upload.text)
            download=self.client.get(url+'/'+upload.json()['id'])
            self.assertEqual(download.status_code,200,download.text)
            self.assertEqual(download.content,content)
            self.assertIn('no-store',download.headers['cache-control'])
            self.assertEqual(self.client.post(url,content=b'x'*(5*1024*1024+1),headers={'Content-Type':'application/pdf'}).status_code,413)
