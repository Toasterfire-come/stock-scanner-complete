"""
Custom authentication that accepts Authorization: Bearer <session_key>
and falls back to standard Django session authentication.

This lets API clients send the session key in the Authorization header
when cross-site cookies are restricted or during XHRs that cannot set cookies.
"""

from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


class BearerSessionAuthentication(BaseAuthentication):
    """Authenticate using Authorization: Bearer <session_key> as Django session."""

    keyword = "Bearer"

    def authenticate(self, request: Request) -> Optional[Tuple[object, None]]:
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth:
            # No header; let other authenticators try
            return None

        parts = auth.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        session_key = parts[1].strip()
        if not session_key:
            return None

        # Attempt to load user from session key
        try:
            store = SessionStore(session_key=session_key)
            data = store.load()
            user_id = data.get("_auth_user_id")
            if not user_id:
                return None

            User = get_user_model()
            user = User.objects.filter(pk=user_id).first()
            if user is None:
                return None

            return (user, None)
        except Exception:
            return None

