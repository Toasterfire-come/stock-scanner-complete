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

        # Content Security Policy - Production-ready configuration
        # Allows React app while maintaining security
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # React requires unsafe-eval for dev, unsafe-inline for inline scripts
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Allow Google Fonts and inline styles (React CSS-in-JS)
            "font-src 'self' https://fonts.gstatic.com data:",  # Google Fonts
            "img-src 'self' data: https: blob:",  # Allow images from anywhere (stock charts, logos)
            "connect-src 'self' https://api.tradescanpro.com https://api.retailtradescanner.com wss: ws:",  # API calls and WebSockets
            "frame-ancestors 'none'",  # Prevent clickjacking (stricter than 'self')
            "base-uri 'self'",  # Restrict base tag
            "form-action 'self'",  # Only allow forms to submit to same origin
            "object-src 'none'",  # Block Flash, Java applets
            "upgrade-insecure-requests",  # Automatically upgrade HTTP to HTTPS
        ]

        response.setdefault('Content-Security-Policy', "; ".join(csp_directives))

        # Additional security headers
        response.setdefault('X-Content-Type-Options', 'nosniff')  # Prevent MIME type sniffing
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')  # Control referrer information
        response.setdefault('X-Frame-Options', 'DENY')  # Prevent clickjacking (stricter than SAMEORIGIN)
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=(), payment=()')  # Disable unnecessary features
        response.setdefault('X-XSS-Protection', '1; mode=block')  # Enable XSS filter (legacy browsers)

        # HSTS header for HTTPS enforcement (only in production)
        # Commented out for development - uncomment for production deployment
        # response.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')

        return response
