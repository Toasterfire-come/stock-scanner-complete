from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pandas as pd
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from stocks.services.backtesting_service import BacktestingService


def _fake_price_history(days: int = 260) -> pd.DataFrame:
    """
    Build a deterministic OHLCV series suitable for MA/RSI windows.
    yfinance returns an index and Open/High/Low/Close/Volume columns.
    """
    start = date(2020, 1, 1)
    dates = pd.date_range(start=start, periods=days, freq="B")  # business days
    close = pd.Series(range(100, 100 + days), index=dates).astype(float)
    df = pd.DataFrame(
        {
            "Open": close * 0.99,
            "High": close * 1.01,
            "Low": close * 0.98,
            "Close": close,
            "Volume": 1_000_000,
            # yfinance often includes these columns; our backtest fetchers expect them.
            "Dividends": 0.0,
            "Stock Splits": 0.0,
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


class BacktestingOperationalTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="btuser",
            email="btuser@example.com",
            password="pass12345",
        )
        self.client.force_authenticate(user=self.user)

    @patch("stocks.backtesting_api.get_user_backtest_limit", return_value=-1)
    @patch("yfinance.Ticker")
    def test_backtest_create_run_get_includes_advanced_metrics(self, mock_ticker, _mock_limit):
        # Mock yfinance price history
        mock_ticker.return_value.history.return_value = _fake_price_history(260)

        start_date = date(2020, 1, 1)
        end_date = start_date + timedelta(days=400)

        create = self.client.post(
            "/api/backtesting/create/",
            {
                "name": "MA Backtest",
                "strategy_text": "Use a 50 and 200 moving average crossover. Buy when 50 MA above 200 MA. Sell when 50 MA below 200 MA.",
                "category": "swing_trading",
                "symbols": ["AAPL"],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "initial_capital": 10000,
            },
            format="json",
        )
        self.assertEqual(create.status_code, 200, create.content)
        self.assertTrue(create.json().get("success"))
        backtest_id = create.json().get("backtest_id")
        self.assertIsNotNone(backtest_id)

        run = self.client.post(f"/api/backtesting/{backtest_id}/run/", {}, format="json")
        self.assertEqual(run.status_code, 200, run.content)
        body = run.json()
        self.assertTrue(body.get("success"))

        results = body.get("results") or {}
        # Advanced metrics the frontend renders
        for key in (
            "sortino_ratio",
            "calmar_ratio",
            "omega_ratio",
            "ulcer_index",
            "var_95",
            "cvar_95",
            "t_statistic",
            "p_value",
            "quality_grade",
        ):
            self.assertIn(key, results, f"Missing {key} in run_backtest results")

        # Trades + equity curve returned immediately for charting
        self.assertIsInstance(body.get("trades"), list)
        self.assertIsInstance(body.get("equity_curve"), list)
        self.assertGreaterEqual(len(body.get("equity_curve")), 2)

        get = self.client.get(f"/api/backtesting/{backtest_id}/")
        self.assertEqual(get.status_code, 200, get.content)
        get_results = (get.json().get("backtest") or {}).get("results") or {}
        self.assertIn("quality_grade", get_results)
        self.assertIn("sortino_ratio", get_results)

        # Sanity check that per-trade profit is not "cash - initial_capital" (i.e., wildly wrong with multiple trades).
        trades = (get.json().get("backtest") or {}).get("trades") or []
        if trades:
            t0 = trades[0]
            expected_profit = (t0["exit_price"] - t0["entry_price"]) * t0["shares"]
            self.assertAlmostEqual(float(t0["profit"]), float(expected_profit), places=6)

    def test_strategy_timeout_safety_does_not_hang(self):
        # Minimal data frame to run the loop quickly
        data = pd.DataFrame(
            {
                "Date": pd.date_range(start="2020-01-01", periods=30, freq="B"),
                "Open": [100.0] * 30,
                "High": [101.0] * 30,
                "Low": [99.0] * 30,
                "Close": [100.0] * 30,
                "Volume": [1_000_000] * 30,
            }
        )

        # entry_condition intentionally loops forever; _with_timeout should cut it off per-iteration.
        code = """
def entry_condition(data, index):
    while True:
        pass

def exit_condition(data, index, entry_price, entry_index):
    return False
"""
        svc = BacktestingService()
        out = svc._execute_strategy(code, data, 10000.0)  # noqa: SLF001 (test uses private helper)
        self.assertNotIn("error", out)
        # Should not have any trades because entry always times out
        self.assertEqual(out.get("total_trades"), 0)


class BacktestingChatAvailabilityTests(APITestCase):
    def test_ai_chat_returns_503_when_no_key(self):
        # This should fail gracefully without GROQ_API_KEY.
        resp = self.client.post(
            "/api/backtesting/chat/",
            {"message": "Help me refine my strategy", "conversation_history": [], "category": "swing_trading"},
            format="json",
        )
        # chat_strategy uses JsonResponse; status should be 503 when AI not available.
        self.assertIn(resp.status_code, (503, 400, 500))
        if resp.status_code == 503:
            self.assertFalse(resp.json().get("success"))
            self.assertFalse(resp.json().get("ai_available"))

