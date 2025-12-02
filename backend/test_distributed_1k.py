#!/usr/bin/env python3
"""Quick test with 1000 proxies"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockscanner_django.settings")

import django
django.setup()

# Modify config before import
import distributed_proxy_scanner
distributed_proxy_scanner.CONFIG.max_proxies_to_test = 1000  # Test only 1000 proxies
distributed_proxy_scanner.CONFIG.proxy_validation_workers = 200  # More reasonable
distributed_proxy_scanner.CONFIG.target_tickers = 100  # Small test batch

print("="*70)
print("QUICK TEST: 1000 proxies, 100 tickers")
print("="*70)

# Run main
distributed_proxy_scanner.main()
