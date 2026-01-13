import unittest

from backend.stock_retrieval.realtime_backfill_policy import choose_backfill_tickers


class TestRealtimeBackfillPolicy(unittest.TestCase):
    def test_prioritizes_hot_then_stale(self):
        out = choose_backfill_tickers(
            hot_tickers=["AAPL", "MSFT"],
            stale_tickers=["TSLA", "AAPL", "GOOG"],
            max_tickers=10,
        )
        self.assertEqual(out, ["AAPL", "MSFT", "TSLA", "GOOG"])

    def test_respects_max(self):
        out = choose_backfill_tickers(
            hot_tickers=["AAPL", "MSFT"],
            stale_tickers=["TSLA", "GOOG"],
            max_tickers=2,
        )
        self.assertEqual(out, ["AAPL", "MSFT"])

    def test_zero_max(self):
        out = choose_backfill_tickers(hot_tickers=["AAPL"], stale_tickers=["TSLA"], max_tickers=0)
        self.assertEqual(out, [])

