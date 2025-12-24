"""
Two-Factor Authentication API Endpoints
RESTful API for SMS-based 2FA management.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from stocks.services.twofa_service import TwoFactorAuthService
import hashlib


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_fingerprint(request):
    """Generate device fingerprint from request"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)
    # Simple fingerprint - in production, use more sophisticated method
    fingerprint_data = f"{user_agent}:{ip_address}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def twofa_status(request):
    """
    Get user's 2FA status and configuration.
    """
    status_info = TwoFactorAuthService.get_user_2fa_status(request.user)

    return Response({
        'success': True,
        'twofa': status_info
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_twofa(request):
    """
    Enable 2FA for user.
    Sends verification code to phone number.

    POST data:
    - phone_number: Phone number in E.164 format (e.g., +1234567890)
    """
    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Enable 2FA and send code
    result = TwoFactorAuthService.enable_2fa(
        user=request.user,
        phone_number=phone_number
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message'],
            'backup_codes': result['backup_codes'],  # Store these securely!
            'next_step': 'Verify the code sent to your phone to complete 2FA setup'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_enable_twofa(request):
    """
    Verify code and complete 2FA enablement.

    POST data:
    - code: 6-digit verification code
    """
    code = request.data.get('code')

    if not code:
        return Response({
            'success': False,
            'error': 'Verification code is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    ip_address = get_client_ip(request)

    result = TwoFactorAuthService.verify_and_enable_2fa(
        user=request.user,
        code=code
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_twofa(request):
    """
    Disable 2FA for user.
    Requires verification code or backup code.

    POST data:
    - code: Verification code OR backup code
    """
    code = request.data.get('code')

    if not code:
        return Response({
            'success': False,
            'error': 'Verification code or backup code is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = TwoFactorAuthService.disable_2fa(
        user=request.user,
        code_or_backup=code
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_code(request):
    """
    Send a new verification code.

    POST data:
    - code_type: Type of code (login, sensitive, etc.) - default: 'login'
    """
    code_type = request.data.get('code_type', 'login')
    ip_address = get_client_ip(request)

    result = TwoFactorAuthService.send_verification_code(
        user=request.user,
        code_type=code_type,
        ip_address=ip_address
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_code(request):
    """
    Verify a 2FA code.

    POST data:
    - code: 6-digit verification code
    - code_type: Type of code being verified - default: 'login'
    - trust_device: Whether to trust this device (optional)
    """
    code = request.data.get('code')
    code_type = request.data.get('code_type', 'login')
    trust_device = request.data.get('trust_device', False)
    ip_address = get_client_ip(request)

    if not code:
        return Response({
            'success': False,
            'error': 'Verification code is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = TwoFactorAuthService.verify_code(
        user=request.user,
        code=code,
        code_type=code_type,
        ip_address=ip_address
    )

    if result['success']:
        # Optionally trust device
        if trust_device:
            device_fingerprint = get_device_fingerprint(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_name = request.data.get('device_name', 'Unknown Device')

            TwoFactorAuthService.trust_device(
                user=request.user,
                device_name=device_name,
                device_fingerprint=device_fingerprint,
                user_agent=user_agent,
                ip_address=ip_address
            )

        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message'],
            'locked': result.get('locked', False)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_backup_code(request):
    """
    Verify a backup code.

    POST data:
    - backup_code: Backup code (format: XXXX-XXXX)
    """
    from stocks.models import TwoFactorAuth

    backup_code = request.data.get('backup_code')

    if not backup_code:
        return Response({
            'success': False,
            'error': 'Backup code is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        twofa = TwoFactorAuth.objects.get(user=request.user, is_enabled=True)
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'success': False,
            'error': '2FA is not enabled'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = TwoFactorAuthService.verify_backup_code(twofa, backup_code)

    if result['success']:
        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_backup_codes(request):
    """
    Generate new backup codes.
    Requires verification code first.

    POST data:
    - code: Verification code
    """
    from stocks.models import TwoFactorAuth

    code = request.data.get('code')

    if not code:
        return Response({
            'success': False,
            'error': 'Verification code is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify code first
    ip_address = get_client_ip(request)
    verify_result = TwoFactorAuthService.verify_code(
        user=request.user,
        code=code,
        code_type='sensitive',
        ip_address=ip_address
    )

    if not verify_result['success']:
        return Response({
            'success': False,
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        twofa = TwoFactorAuth.objects.get(user=request.user, is_enabled=True)
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'success': False,
            'error': '2FA is not enabled'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Generate new backup codes
    backup_codes = TwoFactorAuthService.generate_backup_codes(twofa)

    return Response({
        'success': True,
        'message': 'Backup codes regenerated successfully',
        'backup_codes': backup_codes,
        'warning': 'Store these codes securely. They will not be shown again.'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trusted_devices(request):
    """Get list of trusted devices for user"""
    from stocks.models import TrustedDevice

    devices = TrustedDevice.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_used_at')

    devices_data = [
        {
            'id': device.id,
            'name': device.device_name,
            'ip_address': device.ip_address,
            'location': device.location,
            'last_used': device.last_used_at.isoformat(),
            'trust_expires': device.trust_expires_at.isoformat(),
            'total_uses': device.total_uses,
            'is_current': device.device_fingerprint == get_device_fingerprint(request)
        }
        for device in devices
    ]

    return Response({
        'success': True,
        'devices': devices_data,
        'count': len(devices_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trust_current_device(request):
    """
    Trust the current device.

    POST data:
    - device_name: Custom name for device (optional)
    """
    device_name = request.data.get('device_name', 'My Device')
    device_fingerprint = get_device_fingerprint(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)

    result = TwoFactorAuthService.trust_device(
        user=request.user,
        device_name=device_name,
        device_fingerprint=device_fingerprint,
        user_agent=user_agent,
        ip_address=ip_address
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message'],
            'device_id': result['device_id']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_device(request, device_id):
    """Revoke trust for a specific device"""
    result = TwoFactorAuthService.revoke_trusted_device(
        user=request.user,
        device_id=device_id
    )

    if result['success']:
        return Response({
            'success': True,
            'message': result['message']
        })
    else:
        return Response({
            'success': False,
            'error': result['message']
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log(request):
    """
    Get 2FA audit log for user.

    Query params:
    - limit: Number of entries to return (default: 50, max: 200)
    """
    from stocks.models import TwoFactorAuditLog

    limit = min(int(request.GET.get('limit', 50)), 200)

    logs = TwoFactorAuditLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:limit]

    logs_data = [
        {
            'event_type': log.get_event_type_display(),
            'description': log.event_description,
            'success': log.success,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat()
        }
        for log in logs
    ]

    return Response({
        'success': True,
        'logs': logs_data,
        'count': len(logs_data)
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_settings(request):
    """
    Update 2FA settings.

    PUT data:
    - require_on_login: bool
    - require_on_sensitive: bool
    - trusted_devices_enabled: bool
    """
    from stocks.models import TwoFactorAuth

    try:
        twofa = TwoFactorAuth.objects.get(user=request.user, is_enabled=True)
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'success': False,
            'error': '2FA is not enabled'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Update settings
    if 'require_on_login' in request.data:
        twofa.require_on_login = request.data['require_on_login']

    if 'require_on_sensitive' in request.data:
        twofa.require_on_sensitive = request.data['require_on_sensitive']

    if 'trusted_devices_enabled' in request.data:
        twofa.trusted_devices_enabled = request.data['trusted_devices_enabled']

    twofa.save()

    return Response({
        'success': True,
        'message': '2FA settings updated successfully'
    })


@api_view(['POST'])
@permission_classes([])  # No auth - for login process
def check_2fa_required(request):
    """
    Check if 2FA is required for a username.
    Called during login process.

    POST data:
    - username: Username to check
    """
    from django.contrib.auth.models import User
    from stocks.models import TwoFactorAuth

    username = request.data.get('username')

    if not username:
        return Response({
            'success': False,
            'error': 'Username is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        twofa = TwoFactorAuth.objects.get(user=user, is_enabled=True)

        # Check if device is trusted
        device_fingerprint = get_device_fingerprint(request)
        is_trusted = TwoFactorAuthService.is_device_trusted(user, device_fingerprint)

        return Response({
            'success': True,
            'twofa_required': not is_trusted,
            'phone_hint': f'***-***-{twofa.phone_number[-4:]}' if not is_trusted else None
        })

    except (User.DoesNotExist, TwoFactorAuth.DoesNotExist):
        # Don't reveal if user exists
        return Response({
            'success': True,
            'twofa_required': False
        })
