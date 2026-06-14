import unittest

from app import app


class DashboardApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_dashboard_analytics_endpoint(self):
        response = self.client.get('/api/dashboard/analytics')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('selling_series', data)
        self.assertIn('buying_series', data)
        self.assertIn('profit_series', data)
        self.assertIn('insights', data)

    def test_inventory_endpoint_available(self):
        response = self.client.get('/api/inventory')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
