# Partner Analytics Dashboard

## Overview

Complete partner analytics dashboard for tracking referral performance, commissions, and conversions.

## Access Control

### Whitelisted Partner Email
- **Email**: `hamzashehata3000@gmail.com`
- **Partner Code**: `ADAM50`
- **Commission**: 50% on first payment

### How It Works
1. User logs in with whitelisted email
2. Backend automatically maps email to partner code `ADAM50`
3. Frontend route checks email against whitelist
4. Analytics dashboard loads with partner's data

## Features

### 1. Summary Statistics
- **Total Clicks**: Referral link clicks
- **Trials Started**: Users who started trials
- **Purchases**: Completed purchases
- **Total Commission**: Earnings from referrals

### 2. Referral Link Management
- Display referral link: `https://tradescanpro.com/r/ADAM50`
- One-click copy to clipboard
- Code and discount info displayed
- Active/inactive status badge

### 3. Revenue Tracking

#### Current Period
- Total revenue generated
- Your commission earned
- Customer discounts given

#### Lifetime
- All-time revenue
- All-time commission
- All-time discounts

### 4. Performance Charts

#### Performance Over Time
- Line chart with 3 metrics:
  - Clicks (blue)
  - Trials (green)
  - Purchases (orange)
- Interactive tooltips
- Responsive design

#### Conversion Funnel
- Visual funnel showing:
  - Clicks → 100%
  - Trials → X% conversion
  - Purchases → Y% conversion
- Progress bars with percentages

#### Recent Referrals
- List of last 10 referrals
- Customer name/email
- Purchase date
- Purchase amount
- Commission earned
- Status badge (paid/pending)

### 5. Date Range Filtering
- Last 7 Days
- Last 30 Days
- Last 90 Days
- Last Year

### 6. Export Functionality
- Export analytics to CSV
- Includes all key metrics
- Timestamped filename

## Components

### PartnerAnalytics.jsx
Main dashboard component with:
- Data fetching from backend APIs
- Multiple chart visualizations
- Referral link management
- Export functionality
- Responsive layout

### PartnerAnalyticsRoute.jsx
Protected route wrapper with:
- Authentication check
- Email whitelist validation
- Access denied message
- Loading states

## Backend Integration

### API Endpoints Used

1. **GET `/api/partner/analytics/summary`**
   - Query params: `from`, `to`
   - Returns: Summary statistics, revenue, recent referrals

2. **GET `/api/partner/analytics/timeseries`**
   - Query params: `from`, `to`, `interval`
   - Returns: Time-series data for charts

### Authentication
- Requires logged-in user
- Backend validates email against `PARTNER_CODE_BY_EMAIL` mapping
- Returns data only for authorized partners

## Usage

### 1. Add Route to App

In your main routing file (e.g., `App.jsx` or `routes.jsx`):

```jsx
import PartnerAnalyticsRoute from './routes/PartnerAnalyticsRoute';

// In your routes:
<Route path="/partner/analytics" element={<PartnerAnalyticsRoute />} />
```

### 2. Add Navigation Link

For whitelisted partners, add a link in the navigation:

```jsx
import { useAuth } from './contexts/AuthContext';

function Navigation() {
  const { user } = useAuth();

  const isPartner = user?.email === 'hamzashehata3000@gmail.com';

  return (
    <nav>
      {/* ... other nav items ... */}

      {isPartner && (
        <Link to="/partner/analytics">
          Partner Analytics
        </Link>
      )}
    </nav>
  );
}
```

### 3. Access Dashboard

1. Log in with `hamzashehata3000@gmail.com`
2. Navigate to `/partner/analytics`
3. View real-time analytics

## Data Flow

```
1. User logs in with hamzashehata3000@gmail.com
   ↓
2. Frontend route validates email against whitelist
   ↓
3. Dashboard fetches data from backend APIs
   ↓
4. Backend checks PARTNER_CODE_BY_EMAIL mapping
   ↓
5. Backend returns data for partner code ADAM50
   ↓
6. Dashboard renders with real analytics data
```

## Metrics Calculated

### Click-to-Trial Conversion
```
(Trials / Clicks) × 100
```

### Click-to-Purchase Conversion
```
(Purchases / Clicks) × 100
```

### Commission Amount
```
Purchase Amount × 0.50 (50%)
```

### Revenue Attribution
- Tracked via `ReferralClickEvent` (cookie-based)
- Linked via `ReferralTrialEvent` (user signup)
- Finalized via `RevenueTracking` (payment)

## Customization

### Add More Partners

In `backend/stockscanner_django/settings.py`:

```python
PARTNER_CODE_BY_EMAIL = {
    'hamzashehata3000@gmail.com': 'ADAM50',
    'newpartner@example.com': 'PARTNER100',  # Add new partner
}
```

In `frontend/src/routes/PartnerAnalyticsRoute.jsx`:

```javascript
const PARTNER_EMAILS = [
  'hamzashehata3000@gmail.com',
  'newpartner@example.com',  // Add new partner
];
```

### Change Commission Rate

In backend, update the discount code:

```python
from stocks.models import DiscountCode

code = DiscountCode.objects.get(code='ADAM50')
code.discount_percentage = 40.00  # Change to 40%
code.save()
```

### Customize Date Ranges

In `PartnerAnalytics.jsx`, modify the Select options:

```jsx
<SelectContent>
  <SelectItem value="7d">Last 7 Days</SelectItem>
  <SelectItem value="30d">Last 30 Days</SelectItem>
  <SelectItem value="custom">Custom Range</SelectItem>  // Add custom
</SelectContent>
```

## Dependencies

### Required Packages
- `recharts` - For charts (may need to install)
- `react-router-dom` - For routing
- `sonner` - For toast notifications

### Install if missing:
```bash
npm install recharts
```

## Responsive Design

- **Desktop**: Full dashboard with side-by-side cards
- **Tablet**: 2-column grid layout
- **Mobile**: Single column, stacked cards

## Testing

### Test Data
To test with sample data:

1. Create test clicks:
```python
from stocks.models import ReferralClickEvent
ReferralClickEvent.objects.create(
    code='ADAM50',
    session_id='test',
    ip_hash='test_hash',
    user_agent='Mozilla/5.0'
)
```

2. Create test trials:
```python
from stocks.models import ReferralTrialEvent
from django.contrib.auth.models import User

user = User.objects.get(email='test@example.com')
ReferralTrialEvent.objects.create(
    code='ADAM50',
    user=user
)
```

3. Create test revenue:
```python
from stocks.models import RevenueTracking, DiscountCode
from decimal import Decimal

discount = DiscountCode.objects.get(code='ADAM50')
RevenueTracking.objects.create(
    user=user,
    final_amount=Decimal('49.99'),
    discount_code=discount,
    commission_amount=Decimal('24.995'),
    discount_amount=Decimal('24.995')
)
```

## Troubleshooting

### Dashboard shows "Access Denied"
- Verify user is logged in
- Check email matches whitelist: `hamzashehata3000@gmail.com`
- Verify backend mapping in `settings.py`

### No data showing
- Check API endpoints are accessible
- Verify partner code exists in database
- Check for errors in browser console
- Verify backend `PARTNER_CODE_BY_EMAIL` setting

### Charts not rendering
- Ensure `recharts` package is installed
- Check for console errors
- Verify data format from backend

### Export not working
- Check browser console for errors
- Verify browser supports Blob API
- Test with different browsers

## Security

### Access Control
- Route is protected (requires authentication)
- Email whitelist enforced on frontend
- Backend validates email-to-code mapping
- Staff users have override access

### Data Privacy
- Only partner's own data is visible
- No cross-partner data leakage
- IP addresses are hashed
- User emails shown only for own referrals

## Performance

### Optimization
- Data cached in component state
- Refresh only on user action or date change
- Lightweight charts (recharts)
- Lazy loading for route

### Loading States
- Spinner while fetching data
- Skeleton screens (can be added)
- Error boundaries (can be added)

## Future Enhancements

1. **Real-time Updates**: WebSocket for live metrics
2. **Custom Date Ranges**: Date picker for custom periods
3. **PDF Reports**: Generate downloadable reports
4. **Email Reports**: Scheduled email summaries
5. **Goal Tracking**: Set and track referral goals
6. **Payment History**: Detailed commission payout history
7. **Marketing Materials**: Downloadable referral assets
8. **A/B Testing**: Test different referral campaigns

## Support

For issues or questions:
- Email: carter.kiefer2010@outlook.com
- Check backend logs: `backend/logs/django_server.log`
- Check browser console for frontend errors
