import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)

class Command(BaseCommand):
help = "Complete stock data workflow: fetch → export → filter → notify"

def add_arguments(self, parser):
# Import arguments
parser.add_argument('--batch-size', type=int, default=50, help='Number of tickers to process per batch')
parser.add_argument('--max-workers', type=int, default=3, help='Maximum number of worker threads')
parser.add_argument('--use-cache', action='store_true', help='Use caching to reduce API calls')
parser.add_argument('--delay-range', nargs=2, type=float, default=[1.0, 3.0], 
help='Random delay range between requests (min max)')
parser.add_argument('--proxy-list', nargs='*', help='List of proxy URLs to use for rotation')

# Workflow control
parser.add_argument('--skip-fetch', action='store_true', help='Skip data fetching (use existing data)')
parser.add_argument('--skip-export', action='store_true', help='Skip data export')
parser.add_argument('--skip-notifications', action='store_true', help='Skip email notifications')
parser.add_argument('--dry-run-notifications', action='store_true', 
help='Show what notifications would be sent without sending')

# Advanced options
parser.add_argument('--export-format', choices=['web', 'email'], default='web',
help='Data export format')
parser.add_argument('--notification-category', type=str, 
help='Send notifications only for specific category')

def handle(self, *args, **options):
workflow_start = time.time()

self.stdout.write(" Starting Complete Stock Data Workflow")
self.stdout.write("=" * 60)

steps_completed = 0
total_steps = 4 # fetch, export, filter, notify

# Step 1: Fetch Stock Data
if not options['skip_fetch']:
self.stdout.write("\n STEP 1/4: Fetching Stock Data")
self.stdout.write("-" * 40)

try:
call_command(
'import_stock_data_optimized',
batch_size=options['batch_size'],
max_workers=options['max_workers'],
use_cache=options['use_cache'],
delay_range=options['delay_range'],
proxy_list=options.get('proxy_list', []),
auto_export=not options['skip_export'], # Skip export if requested
verbosity=1
)
steps_completed += 1
self.stdout.write(self.style.SUCCESS(" Stock data fetching completed"))

except Exception as e:
self.stdout.write(self.style.ERROR(f" Step 1 failed: {e}"))
return
else:
self.stdout.write("⏭ STEP 1/4: Skipping stock data fetch")
steps_completed += 1

# Step 2: Export Data
if not options['skip_export']:
self.stdout.write("\n STEP 2/4: Exporting Data for Web Filtering")
self.stdout.write("-" * 40)

try:
call_command(
'export_stock_data',
format=options['export_format'],
verbosity=1
)
steps_completed += 1
self.stdout.write(self.style.SUCCESS(" Data export completed"))

except Exception as e:
self.stdout.write(self.style.ERROR(f" Step 2 failed: {e}"))
# Continue with workflow even if export fails
steps_completed += 1
else:
self.stdout.write("⏭ STEP 2/4: Skipping data export")
steps_completed += 1

# Step 3: Data Quality Check
self.stdout.write("\n STEP 3/4: Data Quality Check")
self.stdout.write("-" * 40)

try:
from stocks.models import StockAlert

total_stocks = StockAlert.objects.count()
unsent_stocks = StockAlert.objects.filter(sent=False).count()
recent_stocks = StockAlert.objects.filter(
last_update__isnull=False
).order_by('-last_update')[:5]

self.stdout.write(f" Total stocks in database: {total_stocks}")
self.stdout.write(f" Unsent notifications: {unsent_stocks}")

if recent_stocks:
self.stdout.write(" Recent updates:")
for stock in recent_stocks:
self.stdout.write(
f" • {stock.ticker}: ${stock.current_price:.2f} - {stock.note[:30]}..."
)

steps_completed += 1
self.stdout.write(self.style.SUCCESS(" Data quality check completed"))

except Exception as e:
self.stdout.write(self.style.WARNING(f" Data quality check failed: {e}"))
steps_completed += 1

# Step 4: Send Notifications
if not options['skip_notifications']:
self.stdout.write("\n STEP 4/4: Processing Email Notifications")
self.stdout.write("-" * 40)

try:
if options['dry_run_notifications']:
call_command(
'send_stock_notifications',
dry_run=True,
category=options.get('notification_category'),
verbosity=1
)
else:
call_command(
'send_stock_notifications',
category=options.get('notification_category'),
verbosity=1
)

steps_completed += 1
self.stdout.write(self.style.SUCCESS(" Email notifications processed"))

except Exception as e:
self.stdout.write(self.style.ERROR(f" Step 4 failed: {e}"))
steps_completed += 1
else:
self.stdout.write("⏭ STEP 4/4: Skipping email notifications")
steps_completed += 1

# Workflow Summary
workflow_time = time.time() - workflow_start

self.stdout.write("\n" + "=" * 60)
self.stdout.write(" WORKFLOW SUMMARY")
self.stdout.write("=" * 60)
self.stdout.write(f"⏱ Total time: {int(workflow_time//60)} min {int(workflow_time%60)} sec")
self.stdout.write(f" Steps completed: {steps_completed}/{total_steps}")

if steps_completed == total_steps:
self.stdout.write(self.style.SUCCESS(" Workflow completed successfully!"))
else:
self.stdout.write(self.style.WARNING(f" Workflow partially completed ({steps_completed}/{total_steps} steps)"))

# Next steps guidance
self.stdout.write("\n NEXT STEPS:")
if not options['skip_notifications'] and not options['dry_run_notifications']:
self.stdout.write(" • Check email delivery logs")
self.stdout.write(" • Monitor subscriber engagement")
else:
self.stdout.write(" • Run with notifications: python manage.py stock_workflow")

self.stdout.write(" • Check web filtering interface for new data")
self.stdout.write(" • Schedule this command for automated runs")

# Performance tips
self.stdout.write("\n PERFORMANCE TIPS:")
if options['batch_size'] > 40:
self.stdout.write(" • Consider reducing batch size for better rate limiting")
if not options['use_cache']:
self.stdout.write(" • Enable caching with --use-cache for better performance")
if not options.get('proxy_list'):
self.stdout.write(" • Consider using proxies for higher volume processing")

self.stdout.write("\n Full command reference:")
self.stdout.write(" python manage.py stock_workflow --help")