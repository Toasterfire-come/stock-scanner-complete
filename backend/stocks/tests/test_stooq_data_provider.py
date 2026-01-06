from __future__ import annotations

import os
from datetime import date
from unittest.mock import patch

import pandas as pd
from rest_framework.test import APITestCase

from stocks.services.backtesting_service import BacktestingService


class StooqProviderSmokeTests(APITestCase):
    @patch("stocks.services.stooq_data.requests.get")
    def test_stooq_remote_daily_fetch_path(self, mock_get):
        # Minimal Stooq CSV response
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "Date,Open,High,Low,Close,Volume\n2020-01-02,10,11,9,10.5,1000\n"
        mock_get.return_value.raise_for_status.return_value = None

        prev = os.environ.get("BACKTEST_DATA_PROVIDER")
        os.environ["BACKTEST_DATA_PROVIDER"] = "stooq"
        try:
            svc = BacktestingService()
            df = svc._fetch_historical_data(["AAPL.US"], date(2020, 1, 1), date(2020, 1, 31))  # noqa: SLF001
            self.assertFalse(df.empty)
            self.assertListEqual(list(df.columns), ["Date", "Open", "High", "Low", "Close", "Volume"])
            self.assertIsInstance(df.iloc[0]["Date"], pd.Timestamp)
        finally:
            if prev is None:
                os.environ.pop("BACKTEST_DATA_PROVIDER", None)
            else:
                os.environ["BACKTEST_DATA_PROVIDER"] = prev

