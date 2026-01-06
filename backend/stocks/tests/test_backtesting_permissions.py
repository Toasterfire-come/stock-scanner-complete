from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from stocks.models import BacktestRun


class BacktestingPermissionsTests(APITestCase):
    def _mk_user(self, username="u1", password="pass1234"):
        User = get_user_model()
        return User.objects.create_user(username=username, password=password)

    def test_backtesting_create_requires_auth(self):
        resp = self.client.post("/api/backtesting/create/", {}, format="json")
        self.assertIn(resp.status_code, (401, 403))

    def test_backtesting_create_and_list_scoped_to_user(self):
        u1 = self._mk_user("user1")
        u2 = self._mk_user("user2")

        self.client.force_authenticate(user=u1)

        payload = {
            "name": "Test",
            "strategy_text": "Buy when RSI < 30, sell when RSI > 70",
            "category": "swing_trading",
            "symbols": ["AAPL"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000,
        }
        r1 = self.client.post("/api/backtesting/create/", payload, format="json")
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(r1.json().get("success"))

        # Create one for u2 directly
        BacktestRun.objects.create(
            user=u2,
            name="Other",
            strategy_text="x",
            category="swing_trading",
            symbols=["MSFT"],
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            initial_capital=10000,
            status="pending",
        )

        lst = self.client.get("/api/backtesting/list/")
        self.assertEqual(lst.status_code, 200)
        self.assertTrue(lst.json().get("success"))

        ids = [b["id"] for b in lst.json().get("backtests", [])]
        self.assertTrue(all(BacktestRun.objects.get(id=i).user_id == u1.id for i in ids))

    def test_shared_backtest_is_public(self):
        u1 = self._mk_user("pubuser")
        bt = BacktestRun.objects.create(
            user=u1,
            name="Public BT",
            strategy_text="x",
            category="swing_trading",
            symbols=["AAPL"],
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            initial_capital=10000,
            status="completed",
            is_public=True,
            share_slug="public-bt-abc123",
        )
        self.client.force_authenticate(user=None)
        resp = self.client.get(f"/api/share/backtests/{bt.share_slug}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

