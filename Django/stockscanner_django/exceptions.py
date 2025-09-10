from typing import Optional

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import exceptions, status


def custom_exception_handler(exc, context) -> Optional[Response]:
    """Return consistent JSON and 401 for unauthenticated API requests.

    - Map NotAuthenticated/AuthenticationFailed to 401 with a compact JSON body
    - Defer to DRF for other exceptions
    """
    response = drf_exception_handler(exc, context)

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        payload = {
            'success': False,
            'error_code': 'AUTH_REQUIRED',
            'error': 'Authentication required',
        }
        return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

    return response

