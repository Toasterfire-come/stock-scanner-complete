"""
Two-Factor Authentication Service
SMS-based 2FA using TextBelt integration.
Provides secure two-factor authentication for user accounts.
"""

import hashlib
import secrets
import string
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from stocks.services.textbelt_service import TextBeltService
import logging

logger = logging.getLogger(__name__)


class TwoFactorAuthService:
    """Service for managing two-factor authentication"""

    # Security Constants
    CODE_EXPIRY_MINUTES = 5
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    TRUSTED_DEVICE_DAYS = 30
    BACKUP_CODES_COUNT = 10

    @staticmethod
    def enable_2fa(user, phone_number):
        """
        Enable 2FA for a user and send verification code.

        Args:
            user: User instance
            phone_number: Phone number for 2FA (E.164 format)

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'code_sent': bool,
                'backup_codes': list (only on success)
            }
        """
        from stocks.models import TwoFactorAuth, TwoFactorAuditLog

        try:
            # Create or get 2FA configuration
            twofa, created = TwoFactorAuth.objects.get_or_create(user=user)

            # Update phone number
            twofa.phone_number = phone_number
            twofa.save()

            # Generate and send verification code
            code_result = TwoFactorAuthService.send_verification_code(
                user=user,
                code_type='enable',
                phone_number=phone_number
            )

            if not code_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to send verification code: {code_result.get('error')}",
                    'code_sent': False
                }

            # Generate backup codes
            backup_codes = TwoFactorAuthService.generate_backup_codes(twofa)

            # Log event
            TwoFactorAuditLog.objects.create(
                user=user,
                twofa=twofa,
                event_type='code_sent',
                event_description='2FA enable code sent',
                success=True
            )

            return {
                'success': True,
                'message': f'Verification code sent to {phone_number}. Please verify to complete 2FA setup.',
                'code_sent': True,
                'backup_codes': backup_codes  # Return plaintext codes only once
            }

        except Exception as e:
            logger.error(f"Error enabling 2FA for {user.username}: {str(e)}")
            return {
                'success': False,
                'message': f'Error enabling 2FA: {str(e)}',
                'code_sent': False
            }

    @staticmethod
    def verify_and_enable_2fa(user, code):
        """
        Verify code and fully enable 2FA.

        Args:
            user: User instance
            code: Verification code

        Returns:
            dict: {'success': bool, 'message': str}
        """
        from stocks.models import TwoFactorAuth, TwoFactorCode, TwoFactorAuditLog

        try:
            twofa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            return {'success': False, 'message': '2FA not configured'}

        # Verify code
        verify_result = TwoFactorAuthService.verify_code(user, code, 'enable')

        if verify_result['success']:
            # Enable 2FA
            twofa.is_enabled = True
            twofa.verified_at = timezone.now()
            twofa.save()

            # Log event
            TwoFactorAuditLog.objects.create(
                user=user,
                twofa=twofa,
                event_type='enabled',
                event_description='2FA successfully enabled',
                success=True
            )

            logger.info(f"2FA enabled for {user.username}")

            return {
                'success': True,
                'message': '2FA successfully enabled'
            }
        else:
            return verify_result

    @staticmethod
    def disable_2fa(user, code_or_backup):
        """
        Disable 2FA after verifying code or backup code.

        Args:
            user: User instance
            code_or_backup: Verification code or backup code

        Returns:
            dict: {'success': bool, 'message': str}
        """
        from stocks.models import TwoFactorAuth, TwoFactorAuditLog

        try:
            twofa = TwoFactorAuth.objects.get(user=user, is_enabled=True)
        except TwoFactorAuth.DoesNotExist:
            return {'success': False, 'message': '2FA is not enabled'}

        # Try verifying as regular code first
        verify_result = TwoFactorAuthService.verify_code(user, code_or_backup, 'disable')

        if not verify_result['success']:
            # Try as backup code
            backup_result = TwoFactorAuthService.verify_backup_code(twofa, code_or_backup)
            if not backup_result['success']:
                return {'success': False, 'message': 'Invalid verification code'}

        # Disable 2FA
        twofa.is_enabled = False
        twofa.save()

        # Revoke all trusted devices
        twofa.trusted_devices.update(is_active=False)

        # Log event
        TwoFactorAuditLog.objects.create(
            user=user,
            twofa=twofa,
            event_type='disabled',
            event_description='2FA disabled',
            success=True
        )

        logger.info(f"2FA disabled for {user.username}")

        return {
            'success': True,
            'message': '2FA successfully disabled'
        }

    @staticmethod
    def send_verification_code(user, code_type='login', phone_number=None, ip_address=None):
        """
        Generate and send a verification code via SMS.

        Args:
            user: User instance
            code_type: Type of code (login, enable, disable, sensitive, recovery)
            phone_number: Phone number (if not provided, uses user's 2FA phone)
            ip_address: IP address of request

        Returns:
            dict: {'success': bool, 'message': str, 'code_id': int}
        """
        from stocks.models import TwoFactorAuth, TwoFactorCode

        # Get phone number
        if not phone_number:
            try:
                twofa = TwoFactorAuth.objects.get(user=user)
                phone_number = twofa.phone_number
            except TwoFactorAuth.DoesNotExist:
                return {'success': False, 'message': '2FA not configured'}

        # Generate 6-digit code
        code = TwoFactorCode.generate_code(6)

        # Calculate expiry
        expires_at = timezone.now() + timedelta(minutes=TwoFactorAuthService.CODE_EXPIRY_MINUTES)

        # Get or create TwoFactorAuth
        twofa, created = TwoFactorAuth.objects.get_or_create(user=user)

        # Create code record
        code_record = TwoFactorCode.objects.create(
            twofa=twofa,
            user=user,
            code=code,
            code_type=code_type,
            expires_at=expires_at,
            phone_number=phone_number,
            ip_address=ip_address
        )

        # Send SMS via TextBelt
        message = f"Your TradeScanPro verification code is: {code}. Valid for {TwoFactorAuthService.CODE_EXPIRY_MINUTES} minutes."

        sms_result = TextBeltService.send_sms(
            phone_number=phone_number,
            message=message,
            user=user
        )

        # Update code record
        if sms_result['success']:
            code_record.sms_sent = True
            code_record.sms_sent_at = timezone.now()
            code_record.textbelt_id = sms_result.get('textbelt_id', '')
            code_record.save()

            logger.info(f"2FA code sent to {user.username} for {code_type}")

            return {
                'success': True,
                'message': f'Verification code sent to {phone_number}',
                'code_id': code_record.id
            }
        else:
            return {
                'success': False,
                'message': f"Failed to send SMS: {sms_result.get('error')}",
                'code_id': code_record.id
            }

    @staticmethod
    def verify_code(user, code, code_type='login', ip_address=None):
        """
        Verify a 2FA code.

        Args:
            user: User instance
            code: Verification code to verify
            code_type: Expected code type
            ip_address: IP address of request

        Returns:
            dict: {'success': bool, 'message': str, 'locked': bool}
        """
        from stocks.models import TwoFactorAuth, TwoFactorCode, TwoFactorAuditLog

        try:
            twofa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            return {'success': False, 'message': '2FA not configured', 'locked': False}

        # Check if account is locked
        if twofa.is_locked_out():
            logger.warning(f"2FA verification blocked - account locked: {user.username}")
            return {
                'success': False,
                'message': f'Account is locked due to too many failed attempts. Try again after {twofa.locked_until.strftime("%H:%M")}',
                'locked': True
            }

        # Get valid codes
        valid_codes = TwoFactorCode.objects.filter(
            user=user,
            code=code,
            code_type=code_type,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')

        if not valid_codes.exists():
            # Failed attempt
            twofa.failed_attempts += 1
            twofa.consecutive_failures += 1
            twofa.last_failed_at = timezone.now()

            # Check if should lock account
            if twofa.consecutive_failures >= TwoFactorAuthService.MAX_FAILED_ATTEMPTS:
                twofa.lock_account(TwoFactorAuthService.LOCKOUT_DURATION_MINUTES)

                TwoFactorAuditLog.objects.create(
                    user=user,
                    twofa=twofa,
                    event_type='account_locked',
                    event_description=f'Account locked after {twofa.consecutive_failures} failed attempts',
                    success=False,
                    ip_address=ip_address
                )

                logger.warning(f"Account locked for {user.username} - too many failed 2FA attempts")

                return {
                    'success': False,
                    'message': f'Account locked for {TwoFactorAuthService.LOCKOUT_DURATION_MINUTES} minutes due to too many failed attempts',
                    'locked': True
                }

            twofa.save()

            TwoFactorAuditLog.objects.create(
                user=user,
                twofa=twofa,
                event_type='code_failed',
                event_description='Invalid verification code',
                success=False,
                ip_address=ip_address
            )

            remaining_attempts = TwoFactorAuthService.MAX_FAILED_ATTEMPTS - twofa.consecutive_failures

            return {
                'success': False,
                'message': f'Invalid verification code. {remaining_attempts} attempts remaining.',
                'locked': False
            }

        # Code is valid
        code_record = valid_codes.first()
        code_record.verification_attempts += 1

        # Check max attempts on this code
        if code_record.verification_attempts > code_record.max_attempts:
            code_record.save()
            return {
                'success': False,
                'message': 'This code has been used too many times. Request a new code.',
                'locked': False
            }

        # Mark code as used
        code_record.mark_used()

        # Reset failure counters
        twofa.consecutive_failures = 0
        twofa.total_verifications += 1
        twofa.last_verified_at = timezone.now()
        twofa.save()

        # Log successful verification
        TwoFactorAuditLog.objects.create(
            user=user,
            twofa=twofa,
            event_type='code_verified',
            event_description=f'{code_type} code verified successfully',
            success=True,
            ip_address=ip_address
        )

        logger.info(f"2FA code verified for {user.username} - {code_type}")

        return {
            'success': True,
            'message': 'Code verified successfully',
            'locked': False
        }

    @staticmethod
    def generate_backup_codes(twofa):
        """
        Generate backup codes for account recovery.

        Args:
            twofa: TwoFactorAuth instance

        Returns:
            list: Plaintext backup codes (only returned once)
        """
        from stocks.models import TwoFactorAuditLog

        backup_codes = []
        hashed_codes = []

        for _ in range(TwoFactorAuthService.BACKUP_CODES_COUNT):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            backup_codes.append(formatted_code)
            # Hash for storage
            hashed_codes.append(make_password(formatted_code))

        # Store hashed codes
        twofa.backup_codes = hashed_codes
        twofa.backup_codes_count = len(hashed_codes)
        twofa.save()

        # Log event
        TwoFactorAuditLog.objects.create(
            user=twofa.user,
            twofa=twofa,
            event_type='backup_generated',
            event_description=f'{len(backup_codes)} backup codes generated',
            success=True
        )

        logger.info(f"Backup codes generated for {twofa.user.username}")

        return backup_codes

    @staticmethod
    def verify_backup_code(twofa, backup_code):
        """
        Verify and consume a backup code.

        Args:
            twofa: TwoFactorAuth instance
            backup_code: Backup code to verify

        Returns:
            dict: {'success': bool, 'message': str}
        """
        from stocks.models import TwoFactorAuditLog

        if not twofa.backup_codes:
            return {'success': False, 'message': 'No backup codes available'}

        # Check each hashed code
        for i, hashed_code in enumerate(twofa.backup_codes):
            if check_password(backup_code, hashed_code):
                # Valid backup code - remove it
                twofa.backup_codes.pop(i)
                twofa.backup_codes_count = len(twofa.backup_codes)
                twofa.save()

                # Log event
                TwoFactorAuditLog.objects.create(
                    user=twofa.user,
                    twofa=twofa,
                    event_type='backup_used',
                    event_description=f'Backup code used. {twofa.backup_codes_count} remaining.',
                    success=True
                )

                logger.info(f"Backup code used for {twofa.user.username}")

                return {
                    'success': True,
                    'message': f'Backup code verified. {twofa.backup_codes_count} backup codes remaining.'
                }

        return {'success': False, 'message': 'Invalid backup code'}

    @staticmethod
    def trust_device(user, device_name, device_fingerprint, user_agent, ip_address, location=''):
        """
        Trust a device for a period (30 days default).

        Args:
            user: User instance
            device_name: User-friendly device name
            device_fingerprint: Hashed device fingerprint
            user_agent: Browser user agent
            ip_address: IP address
            location: Optional location

        Returns:
            dict: {'success': bool, 'message': str, 'device_id': int}
        """
        from stocks.models import TwoFactorAuth, TrustedDevice, TwoFactorAuditLog

        try:
            twofa = TwoFactorAuth.objects.get(user=user, is_enabled=True)
        except TwoFactorAuth.DoesNotExist:
            return {'success': False, 'message': '2FA not enabled'}

        if not twofa.trusted_devices_enabled:
            return {'success': False, 'message': 'Trusted devices feature is disabled'}

        # Check if device already exists
        existing_device = TrustedDevice.objects.filter(
            user=user,
            device_fingerprint=device_fingerprint
        ).first()

        if existing_device:
            # Extend trust
            existing_device.extend_trust(TwoFactorAuthService.TRUSTED_DEVICE_DAYS)
            existing_device.total_uses += 1
            existing_device.save()

            logger.info(f"Device trust extended for {user.username}")

            return {
                'success': True,
                'message': 'Device trust extended',
                'device_id': existing_device.id
            }

        # Create new trusted device
        trust_expires_at = timezone.now() + timedelta(days=TwoFactorAuthService.TRUSTED_DEVICE_DAYS)

        device = TrustedDevice.objects.create(
            twofa=twofa,
            user=user,
            device_name=device_name,
            device_fingerprint=device_fingerprint,
            user_agent=user_agent,
            ip_address=ip_address,
            location=location,
            trust_expires_at=trust_expires_at,
            total_uses=1
        )

        # Log event
        TwoFactorAuditLog.objects.create(
            user=user,
            twofa=twofa,
            event_type='device_trusted',
            event_description=f'Device trusted: {device_name}',
            success=True,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint
        )

        logger.info(f"Device trusted for {user.username}: {device_name}")

        return {
            'success': True,
            'message': f'Device trusted for {TwoFactorAuthService.TRUSTED_DEVICE_DAYS} days',
            'device_id': device.id
        }

    @staticmethod
    def is_device_trusted(user, device_fingerprint):
        """
        Check if a device is trusted.

        Args:
            user: User instance
            device_fingerprint: Device fingerprint to check

        Returns:
            bool: Whether device is trusted
        """
        from stocks.models import TrustedDevice

        try:
            device = TrustedDevice.objects.get(
                user=user,
                device_fingerprint=device_fingerprint,
                is_active=True
            )
            return device.is_trusted()
        except TrustedDevice.DoesNotExist:
            return False

    @staticmethod
    def revoke_trusted_device(user, device_id):
        """
        Revoke trust for a device.

        Args:
            user: User instance
            device_id: TrustedDevice ID

        Returns:
            dict: {'success': bool, 'message': str}
        """
        from stocks.models import TrustedDevice, TwoFactorAuditLog

        try:
            device = TrustedDevice.objects.get(id=device_id, user=user)
        except TrustedDevice.DoesNotExist:
            return {'success': False, 'message': 'Device not found'}

        device.is_active = False
        device.save()

        # Log event
        TwoFactorAuditLog.objects.create(
            user=user,
            twofa=device.twofa,
            event_type='device_revoked',
            event_description=f'Device trust revoked: {device.device_name}',
            success=True
        )

        logger.info(f"Device trust revoked for {user.username}: {device.device_name}")

        return {
            'success': True,
            'message': 'Device trust revoked successfully'
        }

    @staticmethod
    def get_user_2fa_status(user):
        """
        Get comprehensive 2FA status for user.

        Args:
            user: User instance

        Returns:
            dict: 2FA status information
        """
        from stocks.models import TwoFactorAuth

        try:
            twofa = TwoFactorAuth.objects.get(user=user)

            return {
                'enabled': twofa.is_enabled,
                'phone_number': twofa.phone_number,
                'verified_at': twofa.verified_at.isoformat() if twofa.verified_at else None,
                'backup_codes_count': twofa.backup_codes_count,
                'require_on_login': twofa.require_on_login,
                'require_on_sensitive': twofa.require_on_sensitive,
                'trusted_devices_enabled': twofa.trusted_devices_enabled,
                'total_verifications': twofa.total_verifications,
                'failed_attempts': twofa.failed_attempts,
                'is_locked': twofa.is_locked_out(),
                'locked_until': twofa.locked_until.isoformat() if twofa.locked_until else None,
                'trusted_devices': [
                    {
                        'id': device.id,
                        'name': device.device_name,
                        'last_used': device.last_used_at.isoformat(),
                        'expires': device.trust_expires_at.isoformat(),
                        'is_active': device.is_active
                    }
                    for device in twofa.trusted_devices.filter(is_active=True)
                ]
            }
        except TwoFactorAuth.DoesNotExist:
            return {
                'enabled': False,
                'message': '2FA not configured'
            }
