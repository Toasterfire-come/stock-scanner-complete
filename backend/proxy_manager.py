#!/usr/bin/env python3
"""
Proxy Manager for OS-Level Proxy Switching
==========================================

Manages OS-level proxy environment variables and switches proxies
when rate limits are detected.
"""

import os
import random
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages OS-level proxy switching"""

    def __init__(self, proxies: List[str] = None):
        """
        Initialize proxy manager

        Args:
            proxies: List of proxy URLs (e.g., ["http://ip:port", ...])
        """
        self.proxies = proxies or []
        self.current_proxy = None
        self.current_index = 0
        self.failed_proxies = set()

        if self.proxies:
            logger.info(f"Initialized with {len(self.proxies)} proxies")
        else:
            logger.info("Initialized without proxies (direct connection)")

    @classmethod
    def from_proxy_pool(cls, proxy_pool):
        """Create ProxyManager from ProxyPool"""
        proxies = []
        for proxy_dict in proxy_pool.proxies:
            # Extract proxy URL from dict
            if isinstance(proxy_dict, dict):
                proxy_url = proxy_dict.get('http') or proxy_dict.get('https')
                if proxy_url:
                    proxies.append(proxy_url)
            elif isinstance(proxy_dict, str):
                proxies.append(proxy_dict)

        return cls(proxies=proxies)

    def set_proxy(self, proxy_url: Optional[str] = None):
        """
        Set OS-level proxy environment variables

        Args:
            proxy_url: Proxy URL to set, or None to clear proxies
        """
        if proxy_url:
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            self.current_proxy = proxy_url
            logger.info(f"Set OS-level proxy: {proxy_url}")
        else:
            # Clear proxy settings
            for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                if key in os.environ:
                    del os.environ[key]
            self.current_proxy = None
            logger.info("Cleared OS-level proxies (using direct connection)")

    def get_next_proxy(self) -> Optional[str]:
        """Get next available proxy from the pool"""
        if not self.proxies:
            return None

        # Try to find a non-failed proxy
        attempts = 0
        max_attempts = len(self.proxies)

        while attempts < max_attempts:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if proxy not in self.failed_proxies:
                return proxy

            attempts += 1

        # All proxies failed, reset failed set and try again
        logger.warning("All proxies marked as failed, resetting...")
        self.failed_proxies.clear()
        return self.proxies[0] if self.proxies else None

    def switch_proxy(self):
        """Switch to next available proxy"""
        next_proxy = self.get_next_proxy()
        if next_proxy:
            self.set_proxy(next_proxy)
            return True
        else:
            logger.warning("No proxies available, using direct connection")
            self.set_proxy(None)
            return False

    def mark_failed(self, proxy_url: str):
        """Mark a proxy as failed"""
        self.failed_proxies.add(proxy_url)
        logger.warning(f"Marked proxy as failed: {proxy_url}")

    def handle_rate_limit(self):
        """
        Handle rate limit by switching to next proxy

        Returns:
            bool: True if switched successfully, False otherwise
        """
        logger.warning("Rate limit detected, switching proxy...")

        if self.current_proxy:
            self.mark_failed(self.current_proxy)

        return self.switch_proxy()

    def clear(self):
        """Clear all OS-level proxy settings"""
        self.set_proxy(None)

    @staticmethod
    def detect_rate_limit(error: Exception) -> bool:
        """
        Detect if error is a rate limit

        Args:
            error: Exception to check

        Returns:
            bool: True if rate limit detected
        """
        error_str = str(error).lower()

        rate_limit_indicators = [
            'rate limit',
            '429',
            'too many requests',
            'invalid crumb',
            'user is unable to access',
            '401',
            'unauthorized'
        ]

        return any(indicator in error_str for indicator in rate_limit_indicators)

    def __enter__(self):
        """Context manager entry"""
        if self.proxies:
            self.switch_proxy()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clear proxies"""
        self.clear()
