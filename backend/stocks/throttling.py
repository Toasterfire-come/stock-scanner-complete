from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class _SafeCacheMixin:
    """Fail-open throttling when cache is unavailable (e.g., Redis down)."""

    def allow_request(self, request, view):  # type: ignore[override]
        try:
            return super().allow_request(request, view)
        except Exception:
            # If cache backend is down, do not block requests
            return True

    def wait(self):  # type: ignore[override]
        try:
            return super().wait()
        except Exception:
            return None


class SafeAnonRateThrottle(_SafeCacheMixin, AnonRateThrottle):
    pass


class SafeUserRateThrottle(_SafeCacheMixin, UserRateThrottle):
    pass

