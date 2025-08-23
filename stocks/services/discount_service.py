"""
Discount and Revenue Tracking Service
Handles REF50 discount codes and marketer commission calculations
"""

from decimal import Decimal
from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone as django_timezone

from ..models import DiscountCode, UserDiscountUsage, RevenueTracking, MonthlyRevenueSummary, UserProfile


class DiscountService:
    """
    Service to handle discount code operations and revenue tracking
    """
    
    @staticmethod
    def validate_discount_code(code, user):
        """
        Validate if a discount code can be used by a user
        
        Returns:
            dict: {
                'valid': bool,
                'discount': DiscountCode object or None,
                'message': str,
                'discount_amount': Decimal,
                'applies_discount': bool
            }
        """
        try:
            discount = DiscountCode.objects.get(code=code.upper(), is_active=True)
        except DiscountCode.DoesNotExist:
            return {
                'valid': False,
                'discount': None,
                'message': 'Invalid discount code',
                'discount_amount': Decimal('0.00'),
                'applies_discount': False
            }
        
        # Prevent stacking: if the user has used any other discount (got savings) before, disallow this one
        has_other_discount_savings = UserDiscountUsage.objects.filter(
            user=user
        ).exclude(
            discount_code=discount
        ).filter(
            total_savings__gt=Decimal('0.00')
        ).exists()
        if has_other_discount_savings:
            return {
                'valid': False,
                'discount': discount,
                'message': 'Cannot combine with other promotions',
                'discount_amount': Decimal('0.00'),
                'applies_discount': False
            }
        
        # Check if user has already used this discount code
        usage, created = UserDiscountUsage.objects.get_or_create(
            user=user,
            discount_code=discount,
            defaults={'total_savings': Decimal('0.00')}
        )
        
        # Determine if discount applies to this payment
        applies_discount = False
        if discount.applies_to_first_payment_only:
            # For first-payment-only discounts, check if user has made any payments with this code
            has_previous_payments = RevenueTracking.objects.filter(
                user=user,
                discount_code=discount
            ).exists()
            applies_discount = not has_previous_payments
        else:
            # For recurring discounts, always apply
            applies_discount = True
        
        return {
            'valid': True,
            'discount': discount,
            'message': 'Valid discount code' if applies_discount else 'Discount code already used',
            'discount_amount': discount.discount_percentage,
            'applies_discount': applies_discount
        }
    
    @staticmethod
    def calculate_discounted_price(original_amount, discount_percentage):
        """
        Calculate the final price after applying discount
        
        Returns:
            dict: {
                'original_amount': Decimal,
                'discount_amount': Decimal,
                'final_amount': Decimal
            }
        """
        original_amount = Decimal(str(original_amount))
        discount_percentage = Decimal(str(discount_percentage))
        
        discount_amount = (original_amount * discount_percentage) / 100
        final_amount = original_amount - discount_amount
        
        return {
            'original_amount': original_amount,
            'discount_amount': discount_amount,
            'final_amount': final_amount
        }
    
    @staticmethod
    @transaction.atomic
    def record_payment(user, original_amount, discount_code=None, payment_date=None):
        """
        Record a payment and handle discount tracking
        
        Args:
            user: User object
            original_amount: Original price before discount
            discount_code: DiscountCode object or None
            payment_date: datetime object or None (defaults to now)
        
        Returns:
            RevenueTracking object
        """
        if payment_date is None:
            payment_date = django_timezone.now()
        
        original_amount = Decimal(str(original_amount))
        
        # Calculate pricing
        if discount_code:
            validation = DiscountService.validate_discount_code(discount_code.code, user)
            if validation['valid'] and validation['applies_discount']:
                if discount_code.code.upper() == 'TRIAL':
                    # Special trial pricing: $1 for the first 7 days
                    final_amount = Decimal('1.00')
                    if original_amount < final_amount:
                        final_amount = original_amount
                    pricing = {
                        'original_amount': original_amount,
                        'discount_amount': (original_amount - final_amount),
                        'final_amount': final_amount
                    }
                    revenue_type = 'discount_generated'
                else:
                    pricing = DiscountService.calculate_discounted_price(
                        original_amount, 
                        discount_code.discount_percentage
                    )
                    revenue_type = 'discount_generated'
            else:
                # Code exists but doesn't apply discount (already used)
                pricing = {
                    'original_amount': original_amount,
                    'discount_amount': Decimal('0.00'),
                    'final_amount': original_amount
                }
                revenue_type = 'discount_generated'  # Still track as discount-generated for commission
        else:
            pricing = {
                'original_amount': original_amount,
                'discount_amount': Decimal('0.00'),
                'final_amount': original_amount
            }
            revenue_type = 'regular'
        
        # Create revenue tracking record
        revenue_record = RevenueTracking.objects.create(
            user=user,
            discount_code=discount_code,
            revenue_type=revenue_type,
            original_amount=pricing['original_amount'],
            discount_amount=pricing['discount_amount'],
            final_amount=pricing['final_amount'],
            payment_date=payment_date
        )
        
        # Update user discount usage if discount was applied
        if discount_code and pricing['discount_amount'] > 0:
            usage, created = UserDiscountUsage.objects.get_or_create(
                user=user,
                discount_code=discount_code,
                defaults={'total_savings': Decimal('0.00')}
            )
            usage.total_savings += pricing['discount_amount']
            usage.save()
        
        # If trial, set next billing date to 7 days later
        if discount_code and discount_code.code.upper() == 'TRIAL':
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.next_billing_date = payment_date + timedelta(days=7)
            profile.save()
        
        # Update monthly summary
        DiscountService.update_monthly_summary(payment_date.strftime('%Y-%m'))
        
        return revenue_record
    
    @staticmethod
    def update_monthly_summary(month_year):
        """
        Update or create monthly revenue summary for given month
        
        Args:
            month_year: String in format "YYYY-MM"
        """
        # Get all revenue records for the month
        revenue_records = RevenueTracking.objects.filter(month_year=month_year)
        
        # Calculate totals
        totals = revenue_records.aggregate(
            total_revenue=Sum('final_amount'),
            total_discount_savings=Sum('discount_amount'),
            total_commission=Sum('commission_amount')
        )
        
        # Ensure no None values (aggregate can return None if no records)
        totals['total_revenue'] = totals['total_revenue'] or Decimal('0.00')
        totals['total_discount_savings'] = totals['total_discount_savings'] or Decimal('0.00')
        totals['total_commission'] = totals['total_commission'] or Decimal('0.00')
        
        # Calculate revenue breakdown
        regular_revenue = revenue_records.filter(
            revenue_type='regular'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
        
        discount_generated_revenue = revenue_records.filter(
            revenue_type='discount_generated'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
        
        # Calculate user counts
        total_paying_users = revenue_records.values('user').distinct().count()
        
        # Count new vs existing discount users
        discount_users_this_month = revenue_records.filter(
            revenue_type='discount_generated'
        ).values('user', 'discount_code').distinct()
        
        new_discount_users = 0
        existing_discount_users = 0
        
        for record in discount_users_this_month:
            user_id = record['user']
            discount_code_id = record['discount_code']
            
            # Check if this user used this discount code before this month
            first_usage = UserDiscountUsage.objects.filter(
                user_id=user_id,
                discount_code_id=discount_code_id
            ).first()
            
            if first_usage and first_usage.first_used_date.strftime('%Y-%m') == month_year:
                new_discount_users += 1
            else:
                existing_discount_users += 1
        
        # Update or create summary
        summary, created = MonthlyRevenueSummary.objects.update_or_create(
            month_year=month_year,
            defaults={
                'total_revenue': totals['total_revenue'],
                'regular_revenue': regular_revenue,
                'discount_generated_revenue': discount_generated_revenue,
                'total_discount_savings': totals['total_discount_savings'],
                'total_commission_owed': totals['total_commission'],
                'total_paying_users': total_paying_users,
                'new_discount_users': new_discount_users,
                'existing_discount_users': existing_discount_users,
            }
        )
        
        return summary
    
    @staticmethod
    def get_revenue_analytics(month_year=None):
        """
        Get comprehensive revenue analytics for a given month or current month
        
        Args:
            month_year: String in format "YYYY-MM" or None for current month
        
        Returns:
            dict: Comprehensive analytics data
        """
        if month_year is None:
            month_year = django_timezone.now().strftime('%Y-%m')
        
        # Get or create summary
        summary = DiscountService.update_monthly_summary(month_year)
        
        # Get detailed breakdown
        revenue_records = RevenueTracking.objects.filter(month_year=month_year)
        
        # Get discount code breakdown
        discount_breakdown = revenue_records.filter(
            revenue_type='discount_generated'
        ).values(
            'discount_code__code',
            'discount_code__discount_percentage'
        ).annotate(
            user_count=Count('user', distinct=True),
            total_revenue=Sum('final_amount'),
            total_discount=Sum('discount_amount'),
            total_commission=Sum('commission_amount')
        ).order_by('-total_revenue')
        
        return {
            'month_year': month_year,
            'summary': {
                'total_revenue': summary.total_revenue,
                'regular_revenue': summary.regular_revenue,
                'discount_generated_revenue': summary.discount_generated_revenue,
                'total_discount_savings': summary.total_discount_savings,
                'total_commission_owed': summary.total_commission_owed,
                'total_paying_users': summary.total_paying_users,
                'new_discount_users': summary.new_discount_users,
                'existing_discount_users': summary.existing_discount_users,
                'commission_percentage': Decimal('20.00'),
            },
            'discount_breakdown': list(discount_breakdown),
            'marketer_commission': {
                'rate': '20%',
                'amount': summary.total_commission_owed,
                'calculation_base': summary.discount_generated_revenue,
            }
        }
    
    @staticmethod
    def initialize_ref50_code():
        """
        Initialize the REF50 discount code if it doesn't exist
        """
        code, created = DiscountCode.objects.get_or_create(
            code='REF50',
            defaults={
                'discount_percentage': Decimal('50.00'),
                'is_active': True,
                'applies_to_first_payment_only': True,
            }
        )
        return code, created

    @staticmethod
    def initialize_trial_code():
        """
        Initialize the TRIAL discount code if it doesn't exist
        TRIAL: $1 for 7 days, applies to first payment only
        """
        code, created = DiscountCode.objects.get_or_create(
            code='TRIAL',
            defaults={
                'discount_percentage': Decimal('0.00'),
                'is_active': True,
                'applies_to_first_payment_only': True,
            }
        )
        return code, created