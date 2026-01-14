import unittest
import time

from backend.stock_retrieval.proxy_pool import (
    ProxyPool,
    candidate_proxy_urls,
    normalize_hostport,
)


class TestProxyHelpers(unittest.TestCase):
    def test_normalize_hostport_strips_scheme(self):
        self.assertEqual(normalize_hostport("http://1.2.3.4:8080"), "1.2.3.4:8080")
        self.assertEqual(normalize_hostport("https://1.2.3.4:8080"), "1.2.3.4:8080")

    def test_candidate_proxy_urls(self):
        self.assertEqual(candidate_proxy_urls("http://1.2.3.4:8080"), ["http://1.2.3.4:8080"])
        self.assertEqual(candidate_proxy_urls("https://1.2.3.4:8080"), ["https://1.2.3.4:8080"])
        self.assertEqual(
            candidate_proxy_urls("1.2.3.4:8080"),
            ["http://1.2.3.4:8080", "https://1.2.3.4:8080"],
        )


class TestProxyPool(unittest.TestCase):
    def test_choose_prefers_successes_then_latency(self):
        pool = ProxyPool(quarantine_seconds=60, failure_quarantine_threshold=1)
        pool.add_many(["http://a:1", "http://b:1", "http://c:1"])

        # record success on b, but high latency
        pool.record_success("http://b:1", latency_ms=500)
        # record success on c, low latency
        pool.record_success("http://c:1", latency_ms=50)

        chosen = pool.choose()
        self.assertEqual(chosen, "http://c:1")

    def test_quarantine_on_failure(self):
        pool = ProxyPool(quarantine_seconds=60, failure_quarantine_threshold=1)
        pool.add_many(["http://a:1"])
        pool.record_failure("http://a:1", "CONNECT 400")

        # Immediately quarantined
        self.assertIsNone(pool.choose())

        # After quarantine window, should be eligible
        now = time.time()
        pool._stats["http://a:1"].quarantined_until_ts = now - 1  # force expiry
        self.assertEqual(pool.choose(), "http://a:1")

    def test_force_quarantine_even_when_threshold_not_met(self):
        pool = ProxyPool(quarantine_seconds=60, failure_quarantine_threshold=3)
        pool.add_many(["http://a:1"])

        # Soft failure: should not quarantine yet (threshold=3)
        pool.record_failure("http://a:1", "timeout")
        self.assertEqual(pool.choose(), "http://a:1")

        # Hard failure: force quarantine immediately
        pool.record_failure_ex("http://a:1", "CONNECT 502", force_quarantine=True)
        self.assertIsNone(pool.choose())

    def test_json_roundtrip_includes_metadata_fields(self):
        pool = ProxyPool()
        s = pool.upsert("http://a:1")
        s.first_seen_ts = 123.0
        s.last_verified_ts = 456.0
        s.supports_https_connect = True
        s.example_ok = True
        s.yahoo_ok = False
        s.yfinance_ok = None
        pool.record_success("http://a:1", latency_ms=50)

        payload = pool.to_json()
        loaded = ProxyPool.from_json(payload)
        s2 = loaded.upsert("http://a:1")
        self.assertEqual(s2.first_seen_ts, 123.0)
        self.assertEqual(s2.last_verified_ts, 456.0)
        self.assertEqual(s2.supports_https_connect, True)
        self.assertEqual(s2.example_ok, True)
        self.assertEqual(s2.yahoo_ok, False)
        self.assertEqual(s2.yfinance_ok, None)
        self.assertGreaterEqual(s2.successes, 1)

