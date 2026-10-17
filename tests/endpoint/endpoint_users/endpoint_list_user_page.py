from tests.helpers.auth import AuthEndpointTestCase


class UserPageTests(AuthEndpointTestCase):
    def test_paginated_v1_and_legacy_array_have_rbac_and_no_password_data(self):
        self.assertEqual(self.client.get('/api/v1/users').status_code,401)
        self.login_as('staff')
        self.assertEqual(self.client.get('/api/v1/users').status_code,403)
        self.login_as()
        response=self.client.get('/api/v1/users?role=staff&limit=1')
        self.assertEqual(response.status_code,200,response.text)
        page=response.json()
        self.assertEqual(page['total'],1)
        self.assertEqual(page['items'][0]['username'],'staff')
        self.assertNotIn('password',response.text)
        self.assertIsInstance(self.client.get('/users').json(),list)
        self.assertEqual(self.client.get('/api/v1/users',params={'q':"' OR 1=1 --"}).json()['total'],0)
        status=self.client.patch('/api/v1/users/'+self.staff_id+'/status',json={'is_active':False})
        self.assertEqual(status.status_code,200,status.text)
        self.assertFalse(status.json()['is_active'])
        self.assertEqual(self.client.get('/api/v1/users?is_active=false').json()['total'],1)
