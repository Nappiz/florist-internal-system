import unittest
from main import create_app


class ApiContractTests(unittest.TestCase):
    def test_prd_dashboard_and_user_status_routes_exist(self):
        paths=create_app().openapi()['paths']
        for path,method in [('/api/v1/dashboard/summary','get'),('/api/v1/dashboard/recent-orders','get'),('/api/v1/dashboard/recent-purchases','get'),('/api/v1/users/{user_id}/status','patch')]:
            self.assertIn(path,set(paths))
            self.assertIn(method,paths[path])
        operations=[operation['operationId'] for methods in paths.values() for method,operation in methods.items() if method in {'get','post','put','patch','delete'}]
        self.assertEqual(len(operations),len(set(operations)))
