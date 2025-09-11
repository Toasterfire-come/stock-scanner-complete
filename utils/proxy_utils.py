#!/usr/bin/env python3
"""
Proxy Utilities Module
Shared utilities for proxy management, validation, and rotation
"""

import time
import random
import logging
import threading
import requests
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse
import json
import re

logger = logging.getLogger(__name__)

class ProxyManager:
    """Advanced proxy manager with health tracking and rotation"""
    
    def __init__(self, 
                 proxy_file: str = 'working_proxies.json',
                 failure_threshold: int = 3,
                 retry_cooldown: int = 300,
                 max_response_time: float = 5.0):
        """
        Initialize proxy manager
        
        Args:
            proxy_file: Path to proxy JSON file
            failure_threshold: Number of failures before blocking a proxy
            retry_cooldown: Seconds before retrying a blocked proxy
            max_response_time: Maximum acceptable response time
        """
        self.proxy_file = proxy_file
        self.failure_threshold = failure_threshold
        self.retry_cooldown = retry_cooldown
        self.max_response_time = max_response_time
        
        # Proxy health tracking with thread safety
        self.proxy_health = defaultdict(lambda: {
            "failures": 0,
            "successes": 0,
            "last_failure": None,
            "last_success": None,
            "blocked": False,
            "response_times": [],
            "avg_response_time": None
        })
        self.proxy_health_lock = threading.Lock()
        
        # Load proxies
        self.proxies = []
        self.load_proxies()
    
    def load_proxies(self, reload: bool = False):
        """Load proxies from file"""
        if reload or not self.proxies:
            try:
                with open(self.proxy_file, 'r') as f:
                    data = json.load(f)
                
                # Handle different JSON formats
                if isinstance(data, list):
                    # Simple list format
                    self.proxies = []
                    for item in data:
                        if isinstance(item, str):
                            proxy = self.normalize_proxy(item)
                            if proxy:
                                self.proxies.append(proxy)
                        elif isinstance(item, dict) and 'proxy' in item:
                            proxy = self.normalize_proxy(item['proxy'])
                            if proxy:
                                self.proxies.append(proxy)
                elif isinstance(data, dict):
                    # Dictionary format
                    if 'proxies' in data:
                        self.proxies = [self.normalize_proxy(p) for p in data['proxies'] if self.normalize_proxy(p)]
                    elif 'working_proxies' in data:
                        self.proxies = [self.normalize_proxy(p) for p in data['working_proxies'] if self.normalize_proxy(p)]
                
                # Remove duplicates while preserving order
                seen = set()
                unique = []
                for proxy in self.proxies:
                    if proxy not in seen:
                        seen.add(proxy)
                        unique.append(proxy)
                self.proxies = unique
                
                logger.info(f"Loaded {len(self.proxies)} unique proxies from {self.proxy_file}")
            except FileNotFoundError:
                logger.warning(f"Proxy file not found: {self.proxy_file}")
                self.proxies = []
            except Exception as e:
                logger.error(f"Error loading proxies: {e}")
                self.proxies = []
    
    @staticmethod
    def normalize_proxy(proxy_str: str) -> Optional[str]:
        """Normalize proxy string format"""
        if not proxy_str or not isinstance(proxy_str, str):
            return None
        
        p = proxy_str.strip()
        if not p:
            return None
        
        # Add scheme if missing
        if '://' not in p:
            p = f"http://{p}"
        
        # Validate format
        try:
            parsed = urlparse(p)
            if parsed.scheme in ['http', 'https', 'socks4', 'socks5'] and parsed.netloc:
                return p
        except:
            pass
        
        return None
    
    def get_healthy_proxy(self, used_proxies: Optional[Set[str]] = None) -> Optional[str]:
        """Get a healthy proxy, avoiding blocked ones"""
        if not self.proxies:
            return None
        
        if used_proxies is None:
            used_proxies = set()
        
        current_time = datetime.now()
        healthy_proxies = []
        
        with self.proxy_health_lock:
            for proxy in self.proxies:
                if proxy in used_proxies:
                    continue
                
                health = self.proxy_health[proxy]
                
                # Check if proxy is blocked and cooldown period has passed
                if health["blocked"]:
                    if health["last_failure"] and \
                       (current_time - health["last_failure"]).total_seconds() > self.retry_cooldown:
                        health["blocked"] = False
                        health["failures"] = 0
                        logger.info(f"Proxy {proxy} cooldown expired, marking as available")
                    else:
                        continue
                
                # Check average response time
                if health["avg_response_time"] and health["avg_response_time"] > self.max_response_time:
                    continue
                
                healthy_proxies.append(proxy)
        
        if not healthy_proxies:
            # If no healthy proxies, try to unblock some
            self.try_unblock_proxies()
            # Return a random proxy as last resort
            return random.choice(self.proxies) if self.proxies else None
        
        # Sort by success rate and response time
        with self.proxy_health_lock:
            def proxy_score(p):
                h = self.proxy_health[p]
                total = h["successes"] + h["failures"]
                success_rate = h["successes"] / total if total > 0 else 0
                avg_time = h["avg_response_time"] or self.max_response_time
                # Higher success rate and lower response time = better score
                return (success_rate * 100) - (avg_time * 10)
            
            healthy_proxies.sort(key=proxy_score, reverse=True)
        
        return healthy_proxies[0]
    
    def mark_proxy_success(self, proxy: str, response_time: Optional[float] = None):
        """Mark a proxy as successful"""
        if not proxy:
            return
        
        with self.proxy_health_lock:
            health = self.proxy_health[proxy]
            health["successes"] += 1
            health["failures"] = 0  # Reset failure count on success
            health["blocked"] = False
            health["last_success"] = datetime.now()
            
            if response_time is not None:
                health["response_times"].append(response_time)
                # Keep only last 10 response times
                if len(health["response_times"]) > 10:
                    health["response_times"] = health["response_times"][-10:]
                # Calculate average
                health["avg_response_time"] = sum(health["response_times"]) / len(health["response_times"])
    
    def mark_proxy_failure(self, proxy: str, reason: str = ""):
        """Mark a proxy as failed"""
        if not proxy:
            return
        
        with self.proxy_health_lock:
            health = self.proxy_health[proxy]
            health["failures"] += 1
            health["last_failure"] = datetime.now()
            
            if health["failures"] >= self.failure_threshold:
                health["blocked"] = True
                logger.warning(f"Proxy {proxy} blocked after {health['failures']} failures. Reason: {reason}")
    
    def try_unblock_proxies(self):
        """Try to unblock proxies that have passed cooldown"""
        current_time = datetime.now()
        unblocked_count = 0
        
        with self.proxy_health_lock:
            for proxy in self.proxies:
                health = self.proxy_health[proxy]
                if health["blocked"] and health["last_failure"]:
                    if (current_time - health["last_failure"]).total_seconds() > self.retry_cooldown:
                        health["blocked"] = False
                        health["failures"] = 0
                        unblocked_count += 1
        
        if unblocked_count > 0:
            logger.info(f"Unblocked {unblocked_count} proxies after cooldown")
    
    def get_proxy_stats(self) -> Dict:
        """Get statistics about proxy health"""
        with self.proxy_health_lock:
            total = len(self.proxies)
            healthy = 0
            blocked = 0
            total_successes = 0
            total_failures = 0
            avg_response_times = []
            
            for proxy in self.proxies:
                health = self.proxy_health[proxy]
                if health["blocked"]:
                    blocked += 1
                else:
                    healthy += 1
                
                total_successes += health["successes"]
                total_failures += health["failures"]
                
                if health["avg_response_time"]:
                    avg_response_times.append(health["avg_response_time"])
            
            overall_avg_response = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
            success_rate = total_successes / (total_successes + total_failures) * 100 if (total_successes + total_failures) > 0 else 0
            
            return {
                "total_proxies": total,
                "healthy_proxies": healthy,
                "blocked_proxies": blocked,
                "total_successes": total_successes,
                "total_failures": total_failures,
                "success_rate": success_rate,
                "avg_response_time": overall_avg_response
            }
    
    def rotate_proxy(self, current_proxy: Optional[str] = None) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        if current_proxy and current_proxy in self.proxies:
            # Get next proxy after current one
            idx = self.proxies.index(current_proxy)
            next_idx = (idx + 1) % len(self.proxies)
            return self.proxies[next_idx]
        else:
            # Return first healthy proxy
            return self.get_healthy_proxy()
    
    def test_proxy(self, proxy: str, test_url: str = "http://httpbin.org/ip", timeout: int = 10) -> Tuple[bool, float]:
        """Test a single proxy"""
        try:
            proxy_dict = {
                'http': proxy,
                'https': proxy
            }
            
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxy_dict,
                timeout=timeout,
                verify=False,
                allow_redirects=False
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 301, 302]:
                return True, response_time
            
            return False, 0
        except Exception as e:
            logger.debug(f"Proxy test failed for {proxy}: {e}")
            return False, 0
    
    def batch_test_proxies(self, num_threads: int = 20) -> Dict[str, Dict]:
        """Test all proxies in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def test_wrapper(proxy):
            success, response_time = self.test_proxy(proxy)
            return proxy, success, response_time
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(test_wrapper, proxy) for proxy in self.proxies]
            
            for future in as_completed(futures):
                try:
                    proxy, success, response_time = future.result(timeout=15)
                    results[proxy] = {
                        "working": success,
                        "response_time": response_time,
                        "tested_at": datetime.now().isoformat()
                    }
                    
                    if success:
                        self.mark_proxy_success(proxy, response_time)
                    else:
                        self.mark_proxy_failure(proxy, "Test failed")
                except Exception as e:
                    logger.debug(f"Test error: {e}")
        
        return results


class ProxyRotator:
    """Simple proxy rotator for sequential proxy usage"""
    
    def __init__(self, proxies: List[str]):
        self.proxies = proxies
        self.current_index = 0
        self.lock = threading.Lock()
    
    def get_next(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        with self.lock:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy
    
    def reset(self):
        """Reset rotation to beginning"""
        with self.lock:
            self.current_index = 0


def create_proxy_session(proxy: str, timeout: int = 10) -> requests.Session:
    """Create a requests session configured with proxy"""
    session = requests.Session()
    
    # Configure proxy
    proxy_dict = {
        'http': proxy,
        'https': proxy
    }
    session.proxies.update(proxy_dict)
    
    # Configure retries
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set timeout
    session.timeout = timeout
    
    # Disable SSL warnings
    session.verify = False
    
    return session


def extract_proxies_from_text(text: str, default_protocol: str = "http") -> List[str]:
    """Extract proxy addresses from text using regex"""
    proxies = []
    
    # Pattern for IP:PORT
    ip_port_pattern = r'\b(\d{1,3}\.){3}\d{1,3}:\d{1,5}\b'
    matches = re.findall(ip_port_pattern, text)
    
    for match in matches:
        # Add protocol if not present
        if '://' not in match:
            proxy = f"{default_protocol}://{match}"
        else:
            proxy = match
        
        # Validate format
        try:
            parsed = urlparse(proxy)
            if parsed.scheme and parsed.netloc:
                proxies.append(proxy)
        except:
            continue
    
    return proxies


def load_proxies_from_multiple_files(file_paths: List[str]) -> List[str]:
    """Load and merge proxies from multiple files"""
    all_proxies = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                all_proxies.extend(data)
            elif isinstance(data, dict):
                if 'proxies' in data:
                    all_proxies.extend(data['proxies'])
                elif 'working_proxies' in data:
                    all_proxies.extend(data['working_proxies'])
        except Exception as e:
            logger.warning(f"Error loading proxies from {file_path}: {e}")
    
    # Normalize and deduplicate
    normalized = []
    seen = set()
    
    for proxy in all_proxies:
        if isinstance(proxy, str):
            p = ProxyManager.normalize_proxy(proxy)
            if p and p not in seen:
                seen.add(p)
                normalized.append(p)
        elif isinstance(proxy, dict) and 'proxy' in proxy:
            p = ProxyManager.normalize_proxy(proxy['proxy'])
            if p and p not in seen:
                seen.add(p)
                normalized.append(p)
    
    return normalized


def save_proxy_stats(stats: Dict, filename: str = "proxy_stats.json"):
    """Save proxy statistics to file"""
    try:
        stats['timestamp'] = datetime.now().isoformat()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved proxy stats to {filename}")
    except Exception as e:
        logger.error(f"Error saving proxy stats: {e}")