import asyncio
from tempfile import TemporaryDirectory
from pathlib import Path
from tests.helpers.operational_expenses import *
from use_cases.operational_expenses.upload_receipt import upload_receipt
from use_cases.operational_expenses.download_receipt import download_receipt

async def chunks(content):
    yield content

class ReceiptTest(OperationalExpenseTestCase):
    def test_private_storage_type_size_and_ownership(self):
        row=self.create()
        with TemporaryDirectory() as directory, patch('services.expense_receipt_storage.get_settings',return_value=SimpleNamespace(private_receipt_dir=Path(directory))):
            with self.assertRaises(HTTPException): asyncio.run(upload_receipt(self.db,self.staff,row['id'],chunks(b'not-a-png'),'image/png'))
            with self.assertRaises(HTTPException) as error: asyncio.run(upload_receipt(self.db,self.staff,row['id'],chunks(b'x'*(5*1024*1024+1)),'application/pdf'))
            self.assertEqual(error.exception.status_code,413)
            receipt=asyncio.run(upload_receipt(self.db,self.staff,row['id'],chunks(b'%PDF-1.4 test'),'application/pdf'))
            path,mime,_=download_receipt(self.db,self.staff,row['id'],receipt['id'])
            self.assertEqual(path.read_bytes(),b'%PDF-1.4 test')
            self.assertEqual(mime,'application/pdf')
            self.assertNotIn('storage_name',receipt)
            with self.assertRaises(HTTPException): download_receipt(self.db,self.other,row['id'],receipt['id'])
            with self.assertRaises(HTTPException): download_receipt(self.db,self.staff,uuid4(),receipt['id'])
