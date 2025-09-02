#!/usr/bin/env python3

import sys
import os
sys.path.append('/app/backend')

from server import external_api

# Test the external API client with fallback data
fallback_data = {
    "success": True,
    "data": [{"ticker": "TEST", "price": 100}],
    "count": 1
}

try:
    print("Testing external API client...")
    result = external_api.get("/api/stocks/", params={"limit": 3}, fallback_data=fallback_data)
    print("Result:", result)
except Exception as e:
    print("Error:", str(e))