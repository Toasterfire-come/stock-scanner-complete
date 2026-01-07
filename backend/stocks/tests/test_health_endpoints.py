from rest_framework.test import APITestCase


class HealthEndpointsTests(APITestCase):
    def test_api_health_smoke(self):
        r = self.client.get("/api/health/")
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        self.assertEqual(body.get("status"), "healthy")
        self.assertIn("checks", body)
        self.assertIn("metrics", body)

    def test_api_ready_smoke(self):
        r = self.client.get("/api/health/ready/")
        # In CI, DB should be available.
        self.assertIn(r.status_code, (200, 503), r.content)
        body = r.json()
        self.assertIn("ready", body)

    def test_api_live_smoke(self):
        r = self.client.get("/api/health/live/")
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        self.assertIn("alive", body)

