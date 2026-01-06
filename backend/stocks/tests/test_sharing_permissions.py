from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from stocks.models import Stock, UserPortfolio, PortfolioHolding, UserWatchlist, WatchlistItem, SharedResourceLink


class SharingPermissionsTests(APITestCase):
    def _mk_user(self, username="u1", password="pass1234"):
        User = get_user_model()
        return User.objects.create_user(username=username, password=password)

    def _mk_stock(self, ticker="AAPL"):
        return Stock.objects.create(
            ticker=ticker,
            symbol=ticker,
            company_name=f"{ticker} Inc",
            name=f"{ticker} Inc",
            exchange="NASDAQ",
            current_price=Decimal("100.00"),
            volume=1000,
        )

    def test_watchlist_share_create_requires_auth(self):
        u1 = self._mk_user("wluser")
        wl = UserWatchlist.objects.create(user=u1, name="My Watchlist", description="")
        resp = self.client.post(f"/api/share/watchlists/{wl.id}/create")
        self.assertIn(resp.status_code, (401, 403))

    def test_watchlist_share_public_and_copy_flow(self):
        u1 = self._mk_user("wlowner")
        stock = self._mk_stock("AAPL")
        wl = UserWatchlist.objects.create(user=u1, name="My Watchlist", description="d")
        WatchlistItem.objects.create(
            watchlist=wl,
            stock=stock,
            added_price=Decimal("90.00"),
            current_price=Decimal("100.00"),
            price_change=Decimal("10.00"),
            price_change_percent=Decimal("11.11"),
        )

        self.client.force_authenticate(user=u1)
        create = self.client.post(f"/api/share/watchlists/{wl.id}/create")
        self.assertEqual(create.status_code, 200)
        body = create.json()
        self.assertTrue(body.get("success"))
        slug = body.get("slug")
        self.assertTrue(slug)

        # Public page should be accessible without auth
        self.client.force_authenticate(user=None)
        pub = self.client.get(f"/api/share/watchlists/{slug}/")
        self.assertEqual(pub.status_code, 200)
        self.assertTrue(pub.json().get("success"))

        # Copy requires auth
        copy_unauth = self.client.post(f"/api/share/watchlists/{slug}/copy")
        self.assertIn(copy_unauth.status_code, (401, 403))

        u2 = self._mk_user("wlcopy")
        self.client.force_authenticate(user=u2)
        copy = self.client.post(f"/api/share/watchlists/{slug}/copy")
        self.assertEqual(copy.status_code, 200)
        self.assertTrue(copy.json().get("success"))

    def test_portfolio_share_create_and_revoke(self):
        u1 = self._mk_user("powner")
        stock = self._mk_stock("MSFT")
        p = UserPortfolio.objects.create(user=u1, name="My Portfolio", description="d", is_public=False)
        PortfolioHolding.objects.create(
            portfolio=p,
            stock=stock,
            shares=Decimal("1.0"),
            average_cost=Decimal("90.00"),
            current_price=Decimal("100.00"),
            market_value=Decimal("100.00"),
        )

        # Create share requires auth
        self.client.force_authenticate(user=None)
        unauth = self.client.post(f"/api/share/portfolios/{p.id}/create")
        self.assertIn(unauth.status_code, (401, 403))

        self.client.force_authenticate(user=u1)
        create = self.client.post(f"/api/share/portfolios/{p.id}/create")
        self.assertEqual(create.status_code, 200)
        body = create.json()
        self.assertTrue(body.get("success"))
        slug = body.get("slug")
        self.assertTrue(slug)

        # Portfolio should be marked public
        p.refresh_from_db()
        self.assertTrue(p.is_public)

        # Public access works
        self.client.force_authenticate(user=None)
        pub = self.client.get(f"/api/share/portfolios/{slug}/")
        self.assertEqual(pub.status_code, 200)
        self.assertTrue(pub.json().get("success"))

        # Revoke should turn off is_public
        self.client.force_authenticate(user=u1)
        revoke = self.client.post(f"/api/share/portfolios/{p.id}/revoke")
        self.assertEqual(revoke.status_code, 200)
        self.assertTrue(revoke.json().get("success"))
        p.refresh_from_db()
        self.assertFalse(p.is_public)

        # Public endpoint is still accessible by slug (link exists), but UI should treat as private
        # Current backend behavior still serves by slug regardless of is_public. Ensure link exists and responds.
        self.client.force_authenticate(user=None)
        pub2 = self.client.get(f"/api/share/portfolios/{slug}/")
        self.assertEqual(pub2.status_code, 200)
        self.assertTrue(pub2.json().get("success"))

    def test_trade_journal_crud(self):
        u1 = self._mk_user("journaluser")
        self.client.force_authenticate(user=u1)

        create = self.client.post("/api/journal/", {
            "date": "2026-01-06T00:00:00Z",
            "symbol": "AAPL",
            "type": "long",
            "entry_price": 100,
            "exit_price": 110,
            "shares": 1,
            "status": "win",
            "notes": "test",
            "tags": ["tag1"],
        }, format="json")
        self.assertEqual(create.status_code, 201, msg=str(getattr(create, "content", b"")[:2000]))
        body = create.json()
        self.assertTrue(body.get("success"))
        entry_id = body.get("data", {}).get("id")
        self.assertTrue(entry_id)

        lst = self.client.get("/api/journal/")
        self.assertEqual(lst.status_code, 200)
        self.assertTrue(lst.json().get("success"))
        ids = [e.get("id") for e in lst.json().get("data", [])]
        self.assertIn(entry_id, ids)

        upd = self.client.put(f"/api/journal/{entry_id}/", {"status": "breakeven"}, format="json")
        self.assertEqual(upd.status_code, 200)
        self.assertTrue(upd.json().get("success"))
        self.assertEqual(upd.json().get("data", {}).get("status"), "breakeven")

        delete = self.client.delete(f"/api/journal/{entry_id}/")
        self.assertEqual(delete.status_code, 200)
        self.assertTrue(delete.json().get("success"))

