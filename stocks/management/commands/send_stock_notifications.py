import logging
from django.core.management.base import BaseCommand
from emails.stock_notifications import send_stock_notifications

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Send stock notifications via email based on filtered stock alerts"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', 
            action='store_true', 
            help='Show what would be sent without actually sending emails'
        )
        parser.add_argument(
            '--category', 
            type=str, 
            help='Send notifications only for specific category'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        category_filter = options.get('category')
        
        if dry_run:
            self.stdout.write("🧪 DRY RUN MODE - No emails will be sent")
        
        try:
            # Import here to avoid circular imports
            from stocks.models import StockAlert
            from emails.models import EmailSubscription
            from emails.email_filter import EmailFilter
            
            # Get unsent alerts
            unsent_alerts = StockAlert.objects.filter(sent=False)
            
            if not unsent_alerts.exists():
                self.stdout.write(
                    self.style.WARNING('📭 No new stock alerts to send.')
                )
                return
            
            self.stdout.write(f"📊 Found {unsent_alerts.count()} unsent alerts")
            
            # Process notifications
            if dry_run:
                self._dry_run_notifications(unsent_alerts, category_filter)
            else:
                send_stock_notifications()
                self.stdout.write(
                    self.style.SUCCESS('✅ Stock notifications sent successfully')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send notifications: {e}')
            )
            raise
    
    def _dry_run_notifications(self, alerts, category_filter=None):
        """Show what notifications would be sent without sending them"""
        from collections import defaultdict
        from emails.email_filter import EmailFilter
        from emails.models import EmailSubscription
        
        filter = EmailFilter()
        category_map = defaultdict(list)
        
        # Group alerts by category
        for alert in alerts:
            category = filter.filter_email(alert.note.lower())
            if category != "Uncategorized":
                if not category_filter or category == category_filter:
                    category_map[category].append(alert)
        
        self.stdout.write("\n📋 DRY RUN RESULTS:")
        self.stdout.write("=" * 50)
        
        total_notifications = 0
        
        for category, category_alerts in category_map.items():
            subscribers = EmailSubscription.objects.filter(
                category=category, 
                is_active=True
            )
            
            self.stdout.write(f"\n📂 Category: {category}")
            self.stdout.write(f"   📈 Alerts: {len(category_alerts)}")
            self.stdout.write(f"   👥 Subscribers: {subscribers.count()}")
            
            if subscribers.exists():
                self.stdout.write("   📧 Would send to:")
                for sub in subscribers:
                    self.stdout.write(f"      • {sub.email}")
                    total_notifications += 1
                
                self.stdout.write("   📋 Stock alerts:")
                for alert in category_alerts[:5]:  # Show first 5
                    self.stdout.write(
                        f"      • {alert.ticker}: ${alert.current_price} - {alert.note[:50]}..."
                    )
                if len(category_alerts) > 5:
                    self.stdout.write(f"      ... and {len(category_alerts) - 5} more")
            else:
                self.stdout.write("   ⚠️ No active subscribers")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"📊 Summary: {total_notifications} notifications would be sent")
        
        if not category_map:
            self.stdout.write("⚠️ No categorized alerts found for email sending")