#!/usr/bin/env bash
# Usage: REF_ACTIVE="CODE1,CODE2" ./backend/scripts/referral_profits_report.sh
# Prints total discounted revenue (proxy for profit) per referral code and totals for last month.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$PROJECT_ROOT/backend"

# If you need a venv, activate it here (optional)
# source venv/bin/activate

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings}

python - <<'PYCODE'
import os
import sys
import datetime as dt
from decimal import Decimal

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE','stockscanner_django.settings'))
django.setup()

from stocks.models import RevenueTracking, DiscountCode

start_of_month = dt.date.today().replace(day=1)
last_month_end = start_of_month - dt.timedelta(days=1)
last_month_start = last_month_end.replace(day=1)

# Aggregate totals per referral-style discount code (REF_XXXXX)
qs = RevenueTracking.objects.filter(discount_code__code__startswith='REF_')

per_code = {}
for r in qs.values('discount_code__code').annotate(total_rev_sum=django.db.models.Sum('final_amount')):
    code = r['discount_code__code']
    per_code[code] = Decimal(r['total_rev_sum'] or 0)

# Last month totals for referral-generated revenue
last_month_total = RevenueTracking.objects.filter(
    discount_code__code__startswith='REF_',
    payment_date__date__gte=last_month_start,
    payment_date__date__lte=last_month_end
).aggregate(total=django.db.models.Sum('final_amount'))['total'] or Decimal('0')

# Print report
print("Referral Revenue Report")
print("========================")
for code in sorted(per_code.keys()):
    print(f"{code}: ${per_code[code]:.2f}")
print("------------------------")
print(f"Last month total (referral): ${Decimal(last_month_total):.2f}")
PYCODE