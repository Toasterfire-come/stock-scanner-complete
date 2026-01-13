import unittest

from backend.stock_retrieval.proxy_error_classifier import is_hard_proxy_failure


class TestProxyErrorClassifier(unittest.TestCase):
    def test_empty_not_hard(self):
        self.assertFalse(is_hard_proxy_failure(None))
        self.assertFalse(is_hard_proxy_failure(""))
        self.assertFalse(is_hard_proxy_failure("   "))

    def test_connect_status_codes_hard(self):
        self.assertTrue(is_hard_proxy_failure("Received HTTP code 502 from proxy after CONNECT"))
        self.assertTrue(is_hard_proxy_failure("CONNECT tunnel failed, response 400"))
        self.assertTrue(is_hard_proxy_failure("Proxy Authentication Required (407) during CONNECT"))

    def test_common_network_hard(self):
        self.assertTrue(is_hard_proxy_failure("Connection refused"))
        self.assertTrue(is_hard_proxy_failure("No route to host"))
        self.assertTrue(is_hard_proxy_failure("timed out"))

    def test_non_proxy_error_not_hard(self):
        # Not exhaustive: we mainly want to avoid quarantining on parse/shape issues.
        self.assertFalse(is_hard_proxy_failure("parse error: 'Close' column missing"))

