#!/usr/bin/env python3
"""
Intelligent Dual-Proxy Router with Auto-Restart
Automatically switches between 2 proxies and restarts to get fresh IPs
"""

import time
import boto3
import logging
from typing import Optional, Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualProxyRouter:
    """
    Manages 2 EC2 proxies with intelligent switching and auto-restart.

    When one proxy hits the request limit (default 800), it:
    1. Switches to the other proxy
    2. Restarts the rate-limited proxy to get a new IP
    3. Continues seamlessly

    This gives you unlimited capacity with only 2 instances!
    """

    def __init__(
        self,
        proxy_a_name: str = "proxy-a",
        proxy_b_name: str = "proxy-b",
        region: str = "us-east-1",
        request_limit: int = 800,
        proxy_user: str = "proxyuser",
        proxy_password: str = "YourPassword123",
    ):
        self.proxy_a_name = proxy_a_name
        self.proxy_b_name = proxy_b_name
        self.region = region
        self.request_limit = request_limit
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        # AWS EC2 client
        self.ec2 = boto3.client('ec2', region_name=region)

        # State tracking
        self.active_proxy = 'A'  # Start with proxy A
        self.request_count = 0
        self.proxy_a_ip = None
        self.proxy_b_ip = None
        self.total_requests = 0
        self.total_switches = 0

        # Initialize - get current IPs
        logger.info("Initializing Dual Proxy Router...")
        self._refresh_ips()

        if not self.proxy_a_ip or not self.proxy_b_ip:
            logger.warning("One or both proxies not found. Make sure instances are running.")

    def _get_instance_id(self, name: str) -> Optional[str]:
        """Get EC2 instance ID by tag name"""
        try:
            response = self.ec2.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [name]},
                    {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
                ]
            )

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    return instance['InstanceId']
        except Exception as e:
            logger.error(f"Error getting instance ID for {name}: {e}")

        return None

    def _get_instance_ip(self, instance_id: str) -> Optional[str]:
        """Get public IP of EC2 instance"""
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    return instance.get('PublicIpAddress')
        except Exception as e:
            logger.error(f"Error getting IP for instance {instance_id}: {e}")

        return None

    def _refresh_ips(self):
        """Refresh IP addresses of both proxies"""
        # Get Proxy A IP
        proxy_a_id = self._get_instance_id(self.proxy_a_name)
        if proxy_a_id:
            self.proxy_a_ip = self._get_instance_ip(proxy_a_id)
            if self.proxy_a_ip:
                logger.info(f"✓ Proxy A: {self.proxy_a_ip}")

        # Get Proxy B IP
        proxy_b_id = self._get_instance_id(self.proxy_b_name)
        if proxy_b_id:
            self.proxy_b_ip = self._get_instance_ip(proxy_b_id)
            if self.proxy_b_ip:
                logger.info(f"✓ Proxy B: {self.proxy_b_ip}")

    def _restart_instance(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Restart EC2 instance to get fresh IP address.

        AWS reassigns public IPs on instance restart (without Elastic IP).
        This is the key to unlimited IPs!
        """
        instance_id = self._get_instance_id(name)
        if not instance_id:
            logger.error(f"Instance {name} not found")
            return False, None

        logger.info(f"🔄 Restarting {name} to get fresh IP...")

        try:
            # Stop instance
            self.ec2.stop_instances(InstanceIds=[instance_id])
            logger.info(f"  ⏸  Stopping {name}...")

            # Wait for instance to stop
            waiter = self.ec2.get_waiter('instance_stopped')
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 40}
            )
            logger.info(f"  ✓ {name} stopped")

            # Start instance
            self.ec2.start_instances(InstanceIds=[instance_id])
            logger.info(f"  ▶  Starting {name}...")

            # Wait for instance to start
            waiter = self.ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 40}
            )
            logger.info(f"  ✓ {name} running")

            # Wait for proxy service to initialize (30 seconds)
            logger.info(f"  ⏳ Waiting for Squid proxy to start...")
            time.sleep(30)

            # Get new IP address
            new_ip = self._get_instance_ip(instance_id)
            logger.info(f"  🎉 {name} has fresh IP: {new_ip}")

            return True, new_ip

        except Exception as e:
            logger.error(f"Error restarting {name}: {e}")
            return False, None

    def get_current_proxy(self) -> Optional[str]:
        """Get the currently active proxy URL"""
        if self.active_proxy == 'A':
            ip = self.proxy_a_ip
        else:
            ip = self.proxy_b_ip

        if not ip:
            logger.warning(f"No IP for active proxy {self.active_proxy}")
            return None

        return f"http://{self.proxy_user}:{self.proxy_password}@{ip}:3128"

    def record_request(self) -> bool:
        """
        Record a request and check if we need to switch proxies.

        Returns:
            bool: True if switched proxies, False if continuing with same proxy
        """
        self.request_count += 1
        self.total_requests += 1

        # Check if we've hit the limit
        if self.request_count >= self.request_limit:
            logger.info(f"\n⚠️  Reached {self.request_count} requests on Proxy {self.active_proxy}")
            logger.info(f"🔄 Time to switch proxies...")
            self._switch_proxy()
            return True

        return False

    def _switch_proxy(self):
        """
        Switch to the other proxy and restart the rate-limited one.

        This is the magic that gives unlimited capacity!
        """
        old_proxy = self.active_proxy
        new_proxy = 'B' if old_proxy == 'A' else 'A'

        # Switch to new proxy immediately
        self.active_proxy = new_proxy
        self.request_count = 0
        self.total_switches += 1

        logger.info(f"✓ Switched to Proxy {new_proxy}")
        logger.info(f"  Current IP: {self.get_current_proxy()}")

        # Restart old proxy in background to get fresh IP
        old_name = self.proxy_a_name if old_proxy == 'A' else self.proxy_b_name
        success, new_ip = self._restart_instance(old_name)

        if success:
            # Update IP
            if old_proxy == 'A':
                self.proxy_a_ip = new_ip
            else:
                self.proxy_b_ip = new_ip

            logger.info(f"✓ Proxy {old_proxy} restarted with fresh IP: {new_ip}")
            logger.info(f"✓ Ready as standby for next switch\n")
        else:
            logger.error(f"✗ Failed to restart Proxy {old_proxy}\n")

    def get_status(self) -> Dict:
        """Get current status of the router"""
        return {
            'active_proxy': self.active_proxy,
            'request_count': self.request_count,
            'requests_until_switch': self.request_limit - self.request_count,
            'total_requests': self.total_requests,
            'total_switches': self.total_switches,
            'proxy_a_ip': self.proxy_a_ip,
            'proxy_b_ip': self.proxy_b_ip,
            'current_proxy_url': self.get_current_proxy(),
        }

    def print_status(self):
        """Print current status in a nice format"""
        status = self.get_status()
        print("\n" + "=" * 60)
        print("  DUAL PROXY ROUTER STATUS")
        print("=" * 60)
        print(f"Active Proxy:        Proxy {status['active_proxy']}")
        print(f"Current IP:          {status['current_proxy_url'].split('@')[1].split(':')[0]}")
        print(f"Requests on current: {status['request_count']}")
        print(f"Until switch:        {status['requests_until_switch']}")
        print(f"Total requests:      {status['total_requests']}")
        print(f"Total switches:      {status['total_switches']}")
        print(f"")
        print(f"Proxy A IP:          {status['proxy_a_ip']}")
        print(f"Proxy B IP:          {status['proxy_b_ip']}")
        print("=" * 60 + "\n")


# Singleton pattern - only one router instance
_router_instance = None


def get_router(**kwargs) -> DualProxyRouter:
    """
    Get or create the singleton router instance.

    Usage:
        router = get_router(
            proxy_a_name='proxy-a',
            proxy_b_name='proxy-b',
            request_limit=800
        )
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = DualProxyRouter(**kwargs)
    return _router_instance


# Demo usage
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  DUAL PROXY ROUTER DEMO")
    print("=" * 60 + "\n")

    # Initialize router
    router = DualProxyRouter(
        proxy_a_name='proxy-a',
        proxy_b_name='proxy-b',
        region='us-east-1',
        request_limit=10,  # Low limit for demo
        proxy_user='proxyuser',
        proxy_password='YourPassword123',
    )

    # Show initial status
    router.print_status()

    # Simulate 25 requests (will trigger 2 switches)
    print("Simulating 25 requests...\n")
    for i in range(1, 26):
        # Your actual request code would go here
        # For demo, we just record the request

        switched = router.record_request()

        if switched:
            router.print_status()
        elif i % 5 == 0:
            print(f"  Request {i}: Using Proxy {router.active_proxy} "
                  f"({router.request_count} requests on this proxy)")

    # Final status
    router.print_status()

    print("Demo complete!")
    print(f"Made {router.total_requests} requests using only 2 proxies!")
    print(f"Switched {router.total_switches} times, getting fresh IPs each time.\n")
