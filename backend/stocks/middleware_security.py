from typing import Callable

from django.http import HttpResponse


class SecurityHeadersMiddleware:
    """
    Adds common security headers with safe defaults.
    No environment configuration required; all headers are conservative.
    """

    def __init__(self, get_response: Callable[[object], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Content Security Policy (permissive defaults to avoid breaking inline scripts/styles)
        csp = (
            "default-src 'self' http: https: data: blob:; "
            "img-src 'self' http: https: data: blob:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "connect-src 'self' http: https: data:; "
            "frame-ancestors 'self'; "
            "base-uri 'self'"
        )
        response.setdefault('Content-Security-Policy', csp)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        return response
