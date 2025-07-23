from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sys
import os
import json
import csv
import re
from io import StringIO

# Import Django models for stock search functionality
from stocks.models import StockAlert
from emails.email_filter import EmailFilter
from emails.models import EmailSubscription


subscription_configs = {
    # DVSA
    'dvsa-50': {"heading": "Subscribe to DVSA 50% Alerts", "endpoint": "/subscribe-DVSA-50"},
    'dvsa-100': {"heading": "Subscribe to DVSA 100% Alerts", "endpoint": "/subscribe-DVSA-100"},
    'dvsa-150': {"heading": "Subscribe to DVSA 150% Alerts", "endpoint": "/subscribe-DVSA-150"},

    # Market Cap Increase
    'mc-10-in': {"heading": "Market Cap +10%", "endpoint": "/subscribe-mc-10-in"},
    'mc-20-in': {"heading": "Market Cap +20%", "endpoint": "/subscribe-mc-20-in"},
    'mc-30-in': {"heading": "Market Cap +30%", "endpoint": "/subscribe-mc-30-in"},

    # Market Cap Decrease
    'mc-10-de': {"heading": "Market Cap -10%", "endpoint": "/subscribe-mc-10-de"},
    'mc-20-de': {"heading": "Market Cap -20%", "endpoint": "/subscribe-mc-20-de"},
    'mc-30-de': {"heading": "Market Cap -30%", "endpoint": "/subscribe-mc-30-de"},

    # P/E Increase
    'pe-10-in': {"heading": "P/E +10%", "endpoint": "/subscribe-pe-10-in"},
    'pe-20-in': {"heading": "P/E +20%", "endpoint": "/subscribe-pe-20-in"},
    'pe-30-in': {"heading": "P/E +30%", "endpoint": "/subscribe-pe-30-in"},

    # P/E Decrease
    'pe-10-de': {"heading": "P/E -10%", "endpoint": "/subscribe-pe-10-de"},
    'pe-20-de': {"heading": "P/E -20%", "endpoint": "/subscribe-pe-20-de"},
    'pe-30-de': {"heading": "P/E -30%", "endpoint": "/subscribe-pe-30-de"},

    # Price Decrease
    'price-10-de': {"heading": "Price Drop -10%", "endpoint": "/subscribe-price-10-de"},
    'price-15-de': {"heading": "Price Drop -15%", "endpoint": "/subscribe-price-15-de"},
    'price-20-de': {"heading": "Price Drop -20%", "endpoint": "/subscribe-price-20-de"},
}

def subscription_form(request, category):
    config = subscription_configs.get(category)
    if not config:
        return render(request, "404.html", status=404)
    return render(request, "subscription_form.html", config)

def home(request):
    return render(request, "home.html")



# Add blueprint directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../blueprint')))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "json", "stock_data_export.json"))

def normalize_field_name(field_name):
    return re.sub(r'[^a-zA-Z0-9]', '_', field_name).lower()

def coerce_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def load_json_data():
    """Load data from JSON with fallback to database"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return [
                    {normalize_field_name(k): v for k, v in row.items()}
                    for row in data
                ]
            else:
                print("⚠️ Loaded JSON is not a list.")
                return load_from_database()
    except Exception as e:
        print(f"❌ Error loading JSON: {e}, trying database...")
        return load_from_database()

def load_from_database():
    """Load stock data from database"""
    try:
        from stocks.models import StockAlert
        
        stocks = StockAlert.objects.all()
        data = []
        
        for stock in stocks:
            stock_data = {
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': float(stock.current_price) if stock.current_price else 0,
                'price_change_today': float(stock.price_change_today) if stock.price_change_today else 0,
                'volume_today': int(stock.volume_today) if stock.volume_today else 0,
                'dvav': float(stock.dvav) if stock.dvav else 0,
                'dvsa': float(stock.dvsa) if stock.dvsa else 0,
                'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'note': stock.note or '',
                'last_update': stock.last_update.isoformat() if stock.last_update else ''
            }
            data.append(stock_data)
            
        print(f"📊 Loaded {len(data)} stocks from database")
        return data
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def load_filtered_data(filters):
    data = load_json_data()
    if not filters:
        return data

    filtered_data = data.copy()
    for field, condition in filters.items():
        normalized_field = normalize_field_name(field)
        print("👀 Sample row keys:", list(filtered_data[0].keys()))
        print("🔎 Sample row value for", normalized_field, ":", filtered_data[0].get(normalized_field))
        value = condition.get("value")
        condition_type = condition.get("type")

        print(f"🔍 Filtering field: {normalized_field} with condition: {condition_type} {value}")

        if value is None or condition_type is None:
            continue

        if condition_type in ["greater_than", "less_than"]:
            value = coerce_float(value)
            for row in filtered_data:
                row_val = coerce_float(row.get(normalized_field))
                row[normalized_field] = row_val

            if condition_type == "greater_than":
                filtered_data = [r for r in filtered_data if r[normalized_field] is not None and r[normalized_field] > value]
            elif condition_type == "less_than":
                filtered_data = [r for r in filtered_data if r[normalized_field] is not None and r[normalized_field] < value]

        elif condition_type == "equal_to":
            value = coerce_float(value)
            for row in filtered_data:
                row_val = coerce_float(row.get(normalized_field))
                row[normalized_field] = row_val
            filtered_data = [r for r in filtered_data if r[normalized_field] == value]

        elif condition_type == "contains":
            filtered_data = [r for r in filtered_data if value.lower() in str(r.get(normalized_field, "")).lower()]

    print(f"✅ Matched {len(filtered_data)} results after filtering.")
    return filtered_data

from django.http import HttpResponseBadRequest

@csrf_exempt
def filter_view(request):
    if request.method == 'POST':
        try:
            filters = json.loads(request.body)
            print("✅ Filters received:", filters)
        except Exception as e:
            print("❌ JSON parse error:", e)
            return HttpResponseBadRequest("Invalid JSON")

        try:
            results = load_filtered_data(filters)
            print(f"✅ Returned {len(results)} result(s).")
            return JsonResponse(results, safe=False)
        except Exception as e:
            print("❌ Filter processing error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'filter.html')

# News display view
import json
import os
from django.shortcuts import render

def news_view(request):
    json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../json/news.json")
    )

    articles = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
                articles = [
                    a for a in raw
                    if a.get("headline") and a.get("link") and a.get("first_paragraph")
                ]
            except Exception as e:
                print(f"❌ Failed to load or parse news.json: {e}")

    return render(request, "news.html", {"articles": articles})


# Stock search view
def stock_search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search stocks using Django model
        stocks = StockAlert.objects.filter(
            ticker__icontains=query
        ) | StockAlert.objects.filter(
            company_name__icontains=query
        )
        
        results = [
            {
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'current_price': stock.current_price,
                'sector': getattr(stock, 'sector', 'N/A')
            }
            for stock in stocks[:20]  # Limit to 20 results
        ]
    return render(request, 'search.html', {'results': results, 'query': query})


# Personalized filter view
@csrf_exempt
def filter_view(request):
    if request.method == 'POST':
        try:
            print("📥 Raw request body:", request.body)
            filters = json.loads(request.body)
            print("✅ Filters parsed:", filters)

            results = load_filtered_data(filters)
            print("✅ Matched", len(results), "results.")
            return JsonResponse(results, safe=False)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'filter.html')

# Download filtered CSV using Python's csv module
def download_csv_view(request):
    data = load_filtered_data()
    if not data:
        return HttpResponse("No data to export", content_type="text/plain")

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
    return response

# Refresh backend data (could be admin-only or scheduled)
#def data_refresh_view(request):
 #   retrieve_data.main()
  #  return JsonResponse({"status": "Data updated successfully."})

# Optional: Email-based filter download


def email_filter_view(request):
    if request.method == 'POST':
        filter = EmailFilter()
        category = filter.filter_email("dvsa volume 50")
        return JsonResponse({"status": f"Matched category: {category}"})

@csrf_exempt
def generic_subscribe(request, route_name):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return JsonResponse({'message': 'Invalid email address.'}, status=400)

        # This is where you'd store to DB or send confirmation email
        EmailSubscription.objects.create(email=email, category=route_name)

        return JsonResponse({'message': f'Successfully subscribed {email} to {route_name} alerts.'})

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Malformed JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'Unexpected error: {str(e)}'}, status=500)

def admin_dashboard(request):
    """Admin dashboard for managing the optimized stock system"""
    return render(request, 'admin_dashboard.html')

def subscription_form(request, category):
    """Subscription form view"""
    config = subscription_configs.get(category)
    if not config:
        return render(request, 'subscription_form.html', {
            'error': 'Invalid subscription category'
        })
    
    return render(request, 'subscription_form.html', {
        'heading': config['heading'],
        'endpoint': config['endpoint'],
        'category': category
    })
