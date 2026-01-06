from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class FeatureEndpointsSmokeTests(APITestCase):
    def _mk_user(self, username="u1", password="pass1234", email=None):
        User = get_user_model()
        return User.objects.create_user(
            username=username,
            password=password,
            email=email or f"{username}@example.com",
        )

    # -------------------------
    # Auth / profile
    # -------------------------
    def test_auth_csrf_endpoint(self):
        r = self.client.get("/api/auth/csrf/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get("success"))

    def test_auth_register_and_login_and_logout(self):
        reg = self.client.post("/api/auth/register/", {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "pass12345",
            "first_name": "New",
            "last_name": "User",
        }, format="json")
        self.assertEqual(reg.status_code, 201)
        self.assertTrue(reg.json().get("success"))

        login = self.client.post("/api/auth/login/", {"identifier": "newuser@example.com", "password": "pass12345"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.json().get("success"))

        out = self.client.post("/api/auth/logout/", {}, format="json")
        self.assertEqual(out.status_code, 200)
        self.assertTrue(out.json().get("success"))

    def test_user_profile_get_requires_auth(self):
        r = self.client.get("/api/user/profile/")
        self.assertIn(r.status_code, (401, 403))

    # -------------------------
    # Notifications
    # -------------------------
    def test_notifications_history_requires_auth(self):
        r = self.client.get("/api/notifications/history/")
        self.assertIn(r.status_code, (401, 403))

    def test_notifications_mark_read_requires_auth(self):
        r = self.client.post("/api/notifications/mark-read/", {"mark_all": True}, format="json")
        self.assertIn(r.status_code, (401, 403))

    # -------------------------
    # Education (router-backed)
    # -------------------------
    def test_education_list_endpoints_smoke(self):
        # These should return 200 even if empty.
        r1 = self.client.get("/api/education/courses/")
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.get("/api/education/lessons/")
        self.assertEqual(r2.status_code, 200)
        r3 = self.client.get("/api/education/glossary/")
        self.assertEqual(r3.status_code, 200)

    # -------------------------
    # Value hunter (should not 500)
    # -------------------------
    def test_value_hunter_endpoints_smoke(self):
        # These may legitimately return success:false if no stock universe is loaded,
        # but must not 500 in a way that crashes.
        for path in ("/api/value-hunter/current/", "/api/value-hunter/list/", "/api/value-hunter/top-stocks/"):
            r = self.client.get(path)
            self.assertIn(r.status_code, (200, 404))

    # -------------------------
    # Achievements (auth required)
    # -------------------------
    def test_achievements_requires_auth(self):
        r = self.client.get("/api/achievements/")
        # achievements endpoints use Django @login_required (redirects to login page)
        self.assertIn(r.status_code, (401, 403, 302))

    # -------------------------
    # Exports manager (auth required)
    # -------------------------
    def test_exports_history_requires_auth(self):
        r = self.client.get("/api/exports/history/")
        self.assertIn(r.status_code, (401, 403))

