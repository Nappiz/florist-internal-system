import asyncio
import unittest
from configs.body_limit_middleware import BodyLimitMiddleware

class BodyLimitTests(unittest.TestCase):
    def request(self,path,size):
        async def run():
            sent=[]
            async def app(scope,receive,send):
                message=await receive()
                await send({'type':'http.response.start','status':204,'headers':[]})
                await send({'type':'http.response.body','body':b''})
                self.assertEqual(len(message['body']),size)
            async def receive():return {'type':'http.request','body':b'x'*size,'more_body':False}
            async def send(message):sent.append(message)
            await BodyLimitMiddleware(app)({'type':'http','method':'POST','path':path},receive,send)
            return sent[0]['status']
        return asyncio.run(run())

    def test_large_internal_configuration_does_not_relax_auth_limit(self):
        self.assertEqual(self.request('/api/v1/auth/login',20000),413)
        self.assertEqual(self.request('/api/v1/custom-bouquets/estimate',70000),204)
        self.assertEqual(self.request('/api/v1/cashflow/backfill',70000),204)
        self.assertEqual(self.request('/api/v1/custom-bouquets/estimate',256*1024+1),413)
        self.assertEqual(self.request('/api/v1/expenses/not-valid/receipts',20000),413)
