"""
Authentication API Views for Stock Scanner
Handles user registration, login, and profile management
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
import logging
import uuid

from .models import UserProfile, APIToken

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register_api(request):
    """
    User registration endpoint
    URL: /api/auth/register/
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'error': f'{field} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=data['username']).exists():
            return Response({
                'success': False,
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(email=data['email']).exists():
            return Response({
                'success': False,
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user and profile
        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            # Create user profile with free plan
            profile = UserProfile.objects.create(
                user=user,
                plan='free',
                is_premium=False
            )
            
            # Create API token
            api_token = APIToken.objects.create(user=user)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'plan': profile.plan,
                'api_token': str(api_token.token),
                'is_premium': profile.is_premium
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Registration failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_api(request):
    """
    User login endpoint
    URL: /api/auth/login/
    """
    try:
        data = json.loads(request.body)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        # Get or create API token
        api_token, token_created = APIToken.objects.get_or_create(
            user=user,
            is_active=True,
            defaults={'token': uuid.uuid4()}
        )
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'plan': profile.plan,
                'api_token': str(api_token.token),
                'is_premium': profile.is_premium,
                'limits': profile.get_plan_limits()
            }
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Login failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def user_profile_api(request):
    """
    Get or update user profile
    URL: /api/user/profile/
    """
    try:
        # Get user from token (will be implemented in middleware)
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'plan': 'free', 'is_premium': False}
        )
        
        if request.method == 'GET':
            return Response({
                'success': True,
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'plan': profile.plan,
                    'is_premium': profile.is_premium,
                    'limits': profile.get_plan_limits(),
                    'usage': {
                        'monthly_calls': profile.monthly_api_calls,
                        'daily_calls': profile.daily_api_calls,
                        'last_call': profile.last_api_call.isoformat() if profile.last_api_call else None
                    },
                    'subscription': {
                        'active': profile.subscription_active,
                        'end_date': profile.subscription_end_date.isoformat() if profile.subscription_end_date else None,
                        'trial_used': profile.trial_used
                    }
                }
            })
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            
            user.save()
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Profile API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Profile operation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def change_password_api(request):
    """
    Change user password
    URL: /api/user/change-password/
    """
    try:
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        data = json.loads(request.body)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'success': False,
                'error': 'Current password and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Password change failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)