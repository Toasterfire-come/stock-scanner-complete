"""
API Views for discount codes and revenue tracking
"""

import json
from decimal import Decimal
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator

from .services.discount_service import DiscountService
from .models import DiscountCode, RevenueTracking, MonthlyRevenueSummary
from .security_utils import secure_api_endpoint, validate_user_input


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@secure_api_endpoint
def validate_discount_code(request):
    """
    Validate if a discount code can be used by the current user
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        
        if not code:
            return JsonResponse({
                'error': 'Discount code is required'
            }, status=400)
        
        validation = DiscountService.validate_discount_code(code, request.user)
        
        response_data = {
            'valid': validation['valid'],
            'message': validation['message'],
            'applies_discount': validation['applies_discount']
        }
        
        if validation['valid']:
            response_data.update({
                'code': validation['discount'].code,
                'discount_percentage': float(validation['discount_amount']),
                'description': f"{validation['discount_amount']}% off"
            })
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred while validating the discount code'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@secure_api_endpoint
def apply_discount_code(request):
    """
    Apply a discount code and return the calculated pricing
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        original_amount = data.get('amount')
        
        if not code:
            return JsonResponse({
                'error': 'Discount code is required'
            }, status=400)
        
        if not original_amount:
            return JsonResponse({
                'error': 'Amount is required'
            }, status=400)
        
        try:
            original_amount = Decimal(str(original_amount))
        except (ValueError, TypeError):
            return JsonResponse({
                'error': 'Invalid amount format'
            }, status=400)
        
        validation = DiscountService.validate_discount_code(code, request.user)
        
        if not validation['valid']:
            return JsonResponse({
                'error': validation['message']
            }, status=400)
        
        if validation['applies_discount']:
            pricing = DiscountService.calculate_discounted_price(
                original_amount, 
                validation['discount_amount']
            )
        else:
            pricing = {
                'original_amount': original_amount,
                'discount_amount': Decimal('0.00'),
                'final_amount': original_amount
            }
        
        return JsonResponse({
            'success': True,
            'code': validation['discount'].code,
            'applies_discount': validation['applies_discount'],
            'original_amount': float(pricing['original_amount']),
            'discount_amount': float(pricing['discount_amount']),
            'final_amount': float(pricing['final_amount']),
            'savings_percentage': float(validation['discount_amount']) if validation['applies_discount'] else 0,
            'message': validation['message']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred while applying the discount code'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@secure_api_endpoint
def record_payment(request):
    """
    Record a payment transaction with optional discount code
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        original_amount = data.get('amount')
        discount_code = data.get('discount_code', '').strip()
        payment_date_str = data.get('payment_date')
        
        # Validate required fields
        if not user_id:
            return JsonResponse({
                'error': 'User ID is required'
            }, status=400)
        
        if not original_amount:
            return JsonResponse({
                'error': 'Amount is required'
            }, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found'
            }, status=404)
        
        try:
            original_amount = Decimal(str(original_amount))
        except (ValueError, TypeError):
            return JsonResponse({
                'error': 'Invalid amount format'
            }, status=400)
        
        # Parse payment date
        payment_date = timezone.now()
        if payment_date_str:
            try:
                payment_date = datetime.fromisoformat(payment_date_str.replace('Z', '+00:00'))
            except ValueError:
                return JsonResponse({
                    'error': 'Invalid payment date format'
                }, status=400)
        
        # Get discount code object if provided
        discount_obj = None
        if discount_code:
            try:
                discount_obj = DiscountCode.objects.get(code=discount_code.upper(), is_active=True)
            except DiscountCode.DoesNotExist:
                return JsonResponse({
                    'error': 'Invalid discount code'
                }, status=400)
        
        # Record the payment
        revenue_record = DiscountService.record_payment(
            user=user,
            original_amount=original_amount,
            discount_code=discount_obj,
            payment_date=payment_date
        )
        
        return JsonResponse({
            'success': True,
            'revenue_id': revenue_record.id,
            'original_amount': float(revenue_record.original_amount),
            'discount_amount': float(revenue_record.discount_amount),
            'final_amount': float(revenue_record.final_amount),
            'commission_amount': float(revenue_record.commission_amount),
            'revenue_type': revenue_record.revenue_type,
            'month_year': revenue_record.month_year
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred while recording the payment'
        }, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_revenue_analytics(request, month_year=None):
    """
    Get revenue analytics - supports both HTML and API responses
    WordPress/AJAX calls get JSON, browser visits get HTML page
    """
    try:
        analytics = DiscountService.get_revenue_analytics(month_year)
        
        # Convert Decimal to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return obj
        
        analytics = convert_decimals(analytics)
        
        # Check if this should be an API response
        is_api_request = (
            # WordPress/AJAX requests
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or
            # Accept header indicates JSON
            'application/json' in request.META.get('HTTP_ACCEPT', '') or
            # Explicit format parameter
            request.GET.get('format') == 'json' or
            # Always API for WordPress compatibility
            getattr(request, 'is_api_request', True)  # Default to API for revenue
        )
        
        if is_api_request:
            return JsonResponse({
                'success': True,
                'data': analytics,
                'timestamp': timezone.now().isoformat(),
                'endpoint': request.path,
                'method': request.method
            })
        else:
            # Return HTML page for browser visits
            from django.shortcuts import render
            context = {
                'analytics': analytics,
                'month_year': month_year,
                'title': f'Revenue Analytics - {month_year or "Current"}'
            }
            return render(request, 'revenue/analytics.html', context)
        
    except Exception as e:
        logger.error(f"Error in get_revenue_analytics: {e}")
        
        # Check if this should be an API response for errors too
        is_api_request = (
            request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or
            'application/json' in request.META.get('HTTP_ACCEPT', '') or
            request.GET.get('format') == 'json' or
            getattr(request, 'is_api_request', True)
        )
        
        if is_api_request:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while fetching revenue analytics',
                'timestamp': timezone.now().isoformat(),
                'endpoint': request.path
            }, status=500)
        else:
            from django.shortcuts import render
            context = {
                'error': 'An error occurred while fetching revenue analytics',
                'month_year': month_year
            }
            return render(request, 'revenue/analytics.html', context)


@require_http_methods(["GET"])
@user_passes_test(lambda u: u.is_staff)
def get_monthly_summary(request, month_year):
    """
    Get monthly revenue summary
    """
    try:
        summary = MonthlyRevenueSummary.objects.filter(month_year=month_year).first()
        
        if not summary:
            return JsonResponse({
                'error': 'No data found for the specified month'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'summary': {
                'month_year': summary.month_year,
                'total_revenue': float(summary.total_revenue),
                'regular_revenue': float(summary.regular_revenue),
                'discount_generated_revenue': float(summary.discount_generated_revenue),
                'total_discount_savings': float(summary.total_discount_savings),
                'total_commission_owed': float(summary.total_commission_owed),
                'total_paying_users': summary.total_paying_users,
                'new_discount_users': summary.new_discount_users,
                'existing_discount_users': summary.existing_discount_users,
                'last_updated': summary.last_updated.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred while fetching monthly summary'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def initialize_discount_codes(request):
    """
    Initialize the REF50 discount code - WordPress compatible
    Always returns JSON response
    """
    try:
        code, created = DiscountService.initialize_ref50_code()
        
        return JsonResponse({
            'success': True,
            'data': {
                'code': code.code,
                'discount_percentage': float(code.discount_percentage),
                'created': created,
                'message': 'REF50 code created' if created else 'REF50 code already exists'
            },
            'timestamp': timezone.now().isoformat(),
            'endpoint': request.path,
            'method': request.method
        })
        
    except Exception as e:
        logger.error(f"Error in initialize_discount_codes: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while initializing discount codes',
            'timestamp': timezone.now().isoformat(),
            'endpoint': request.path
        }, status=500)