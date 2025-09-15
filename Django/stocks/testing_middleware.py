"""
Test middleware to bypass authentication locally by injecting a test user.
Only used under settings_testing.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


class TestUserMiddleware(MiddlewareMixin):
    """Set request.user to a known test user for local testing."""

    def process_request(self, request):
        try:
            User = get_user_model()
            email = 'carter.kiefer2010@outlook.com'
            username = 'test_user'
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_active': True,
                }
            )
            request.user = user
        except Exception as e:
            logger.warning(f"TestUserMiddleware failed: {e}")
        return None

