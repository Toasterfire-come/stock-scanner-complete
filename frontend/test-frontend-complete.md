# Complete Frontend Testing Checklist

**Test Date:** ________________
**Tester:** ________________
**Environment:** ________________

---

## 1. Authentication & User Management

### Sign Up Flow
- [ ] Navigate to Sign Up page
- [ ] Test form validation (empty fields)
- [ ] Test email format validation
- [ ] Test password strength requirements
- [ ] Test password confirmation matching
- [ ] Successfully create new account
- [ ] Verify email sent (check console/logs)
- [ ] Verify redirect after signup
- [ ] Test error handling for existing email

### Sign In Flow
- [ ] Navigate to Sign In page
- [ ] Test form validation
- [ ] Test with invalid credentials
- [ ] Test with valid credentials
- [ ] Verify successful login redirect
- [ ] Check auth token stored correctly
- [ ] Test "Remember Me" functionality
- [ ] Test "Forgot Password" link

### Password Reset
- [ ] Click "Forgot Password"
- [ ] Enter email address
- [ ] Verify reset email sent
- [ ] Click reset link
- [ ] Enter new password
- [ ] Confirm password change works
- [ ] Test login with new password

### OAuth/Social Login
- [ ] Test Google Sign-In button appears
- [ ] Test Google OAuth flow (if configured)
- [ ] Verify user created/logged in via OAuth

### Two-Factor Authentication
- [ ] Enable 2FA in settings
- [ ] Verify QR code/setup code shown
- [ ] Enter verification code
- [ ] Test login with 2FA enabled
- [ ] Test backup codes

### Session Management
- [ ] Verify auto-logout on token expiry
- [ ] Test manual logout
- [ ] Verify session persists on page refresh
- [ ] Test concurrent sessions
- [ ] Check protected routes redirect when logged out

---

## 2. Dashboard & Home Page

### Main Dashboard
- [ ] Dashboard loads without errors
- [ ] All widgets render correctly
- [ ] Market status indicator shows current status
- [ ] Top movers section populates
- [ ] Trending stocks section populates
- [ ] Recent alerts display (if any)
- [ ] Portfolio summary shows correct data
- [ ] Charts render correctly

### Market Status
- [ ] Pre-market indicator works
- [ ] Regular hours indicator works
- [ ] After-hours indicator works
- [ ] Closed market indicator works
- [ ] Status updates in real-time

### Quick Actions
- [ ] "Create Screener" button works
- [ ] "Add to Watchlist" works
- [ ] "New Alert" button works
- [ ] Command palette opens (Cmd/Ctrl+K)

### Dashboard Customization
- [ ] Can add/remove widgets
- [ ] Can rearrange widgets (drag & drop)
- [ ] Layout saves to user preferences
- [ ] Reset to default works

---

## 3. Stock Scanner & Screener

### Stock List View
- [ ] Stock list loads and displays
- [ ] Pagination works correctly
- [ ] Sorting by column works
- [ ] Column headers clickable
- [ ] Search/filter functionality
- [ ] Virtual scrolling performance

### Stock Detail Page
- [ ] Navigate to stock detail (e.g., AAPL)
- [ ] Price chart displays correctly
- [ ] Company info section loads
- [ ] Key statistics display
- [ ] Fundamentals tab works
- [ ] News feed shows relevant news
- [ ] Historical data loads

### Price Charts
- [ ] LightweightPriceChart renders
- [ ] Can change timeframe (1D, 1W, 1M, etc.)
- [ ] Can toggle chart types (candlestick, line)
- [ ] Zoom in/out works
- [ ] Tooltips show on hover
- [ ] Indicators can be added/removed
- [ ] Chart export functionality

### Screener Templates
- [ ] Navigate to Screeners page
- [ ] Templates list displays
- [ ] Can preview template criteria
- [ ] Can create screener from template
- [ ] Popular templates highlighted

### Create Custom Screener
- [ ] Click "Create Screener"
- [ ] Add filter criteria (price, volume, etc.)
- [ ] Test AND/OR logic
- [ ] Save screener with name
- [ ] Run screener - results populate
- [ ] Export results to CSV
- [ ] Share screener link

### Screener Results
- [ ] Results table displays correctly
- [ ] Can sort results
- [ ] Can filter results
- [ ] Add stocks to watchlist from results
- [ ] Export results works
- [ ] Pagination works

### Edit/Delete Screener
- [ ] Can edit saved screener
- [ ] Changes save correctly
- [ ] Can delete screener
- [ ] Confirm deletion prompt

---

## 4. Watchlists & Portfolio

### Watchlists
- [ ] Navigate to Watchlists page
- [ ] Create new watchlist
- [ ] Add stocks to watchlist
- [ ] Remove stocks from watchlist
- [ ] Rename watchlist
- [ ] Delete watchlist
- [ ] Multiple watchlists support
- [ ] Watchlist data persists

### Watchlist Detail
- [ ] View individual watchlist
- [ ] Stocks display with current prices
- [ ] Can reorder stocks (drag & drop)
- [ ] Real-time price updates (if enabled)
- [ ] Performance metrics show
- [ ] Export watchlist to CSV

### Share Watchlist
- [ ] Generate shareable link
- [ ] Public link works (open in incognito)
- [ ] Can revoke share link
- [ ] Copy someone else's watchlist

### Portfolio Management
- [ ] Navigate to Portfolio page
- [ ] Add new position
- [ ] Enter purchase price & quantity
- [ ] Edit existing position
- [ ] Close/remove position
- [ ] Portfolio value calculates correctly
- [ ] P&L shows correctly (profit/loss)

### Portfolio Analytics
- [ ] Total portfolio value displays
- [ ] Daily P&L calculates
- [ ] Overall return percentage
- [ ] Allocation chart (pie chart)
- [ ] Performance chart over time
- [ ] Export portfolio to CSV

---

## 5. Alerts & Notifications

### Create Alert
- [ ] Navigate to Alerts page
- [ ] Click "Create Alert"
- [ ] Select stock ticker
- [ ] Set alert condition (price above/below)
- [ ] Set target price
- [ ] Save alert
- [ ] Alert appears in list

### Manage Alerts
- [ ] View all alerts
- [ ] Edit existing alert
- [ ] Delete alert
- [ ] Toggle alert on/off
- [ ] Alert history displays

### Alert Notifications
- [ ] Trigger alert condition
- [ ] Browser notification appears
- [ ] Alert marked as triggered
- [ ] Alert email sent (if configured)
- [ ] SMS sent (if configured)

### Notification Settings
- [ ] Navigate to Notification Settings
- [ ] Toggle email notifications
- [ ] Toggle browser notifications
- [ ] Toggle SMS notifications
- [ ] Set notification preferences
- [ ] Save changes

---

## 6. Billing & Subscriptions

### Plan Selection
- [ ] Navigate to Pricing page
- [ ] Plans display correctly
- [ ] Features comparison visible
- [ ] Select plan (Free/Pro/Premium)
- [ ] Click "Subscribe" button

### PayPal Checkout
- [ ] PayPal button renders
- [ ] Click PayPal button
- [ ] PayPal modal opens
- [ ] Complete payment in sandbox
- [ ] Redirect back to app
- [ ] Success message displays
- [ ] Subscription activated

### Stripe Checkout (if implemented)
- [ ] Stripe payment form renders
- [ ] Enter test card: 4242 4242 4242 4242
- [ ] Complete payment
- [ ] Success confirmation
- [ ] Subscription activated

### Billing History
- [ ] Navigate to Billing History
- [ ] Past payments display
- [ ] Download invoice/receipt
- [ ] Payment details correct

### Plan Management
- [ ] View current plan
- [ ] Upgrade plan
- [ ] Downgrade plan
- [ ] Cancel subscription
- [ ] Confirm cancellation
- [ ] Check cancellation email

### Discount Codes
- [ ] Apply discount code at checkout
- [ ] Verify discount applied
- [ ] Invalid code shows error
- [ ] Expired code handled

---

## 7. News & Market Data

### News Feed
- [ ] Navigate to News page
- [ ] News articles load
- [ ] Can filter by category
- [ ] Can search news
- [ ] Click article - opens detail
- [ ] Sentiment analysis shows (if available)
- [ ] News sources displayed

### Stock-Specific News
- [ ] View stock detail page
- [ ] News tab shows stock news
- [ ] News relevant to ticker
- [ ] Timestamps correct
- [ ] Links open in new tab

### Market Calendar
- [ ] Navigate to Economic Calendar
- [ ] Calendar displays events
- [ ] Can filter by importance
- [ ] Can change date range
- [ ] Event details show on click

---

## 8. Search & Filters

### Global Search
- [ ] Click search icon/bar
- [ ] Type stock ticker (AAPL)
- [ ] Results populate instantly
- [ ] Select result - navigate to stock
- [ ] Search by company name
- [ ] Search suggestions appear

### Advanced Filters
- [ ] Open filter panel
- [ ] Set price range filter
- [ ] Set volume filter
- [ ] Set market cap filter
- [ ] Apply multiple filters
- [ ] Clear filters
- [ ] Save filter preset

---

## 9. Settings & User Profile

### Profile Settings
- [ ] Navigate to Profile/Settings
- [ ] Update display name
- [ ] Update email
- [ ] Upload profile picture
- [ ] Save changes
- [ ] Changes persist

### Account Settings
- [ ] Change password
- [ ] Update notification preferences
- [ ] Set default watchlist
- [ ] Set timezone
- [ ] Set currency preference
- [ ] Save settings

### Privacy Settings
- [ ] Make profile public/private
- [ ] Show/hide portfolio
- [ ] Show/hide watchlists
- [ ] Data sharing preferences

### API Keys (Developer)
- [ ] Navigate to Developer Console
- [ ] Generate API key
- [ ] View API documentation
- [ ] Test API endpoint
- [ ] Revoke API key
- [ ] Usage statistics display

---

## 10. Responsive Design & Mobile

### Mobile Layout (< 768px)
- [ ] Open app on mobile device/resize browser
- [ ] Hamburger menu appears
- [ ] Navigation drawer works
- [ ] Dashboard adapts to mobile
- [ ] Charts resize appropriately
- [ ] Tables scroll horizontally
- [ ] Forms usable on mobile

### Tablet Layout (768px - 1024px)
- [ ] Layout adapts for tablet
- [ ] Side navigation behavior
- [ ] Charts display correctly
- [ ] Touch interactions work

### Desktop (> 1024px)
- [ ] Full layout displays
- [ ] Sidebar navigation
- [ ] Multi-column layouts
- [ ] Charts full-sized

---

## 11. Performance & UX

### Page Load Performance
- [ ] Initial page load < 3 seconds
- [ ] Dashboard loads quickly
- [ ] Stock detail page loads quickly
- [ ] No console errors on load
- [ ] Images/icons load

### Real-Time Updates
- [ ] Stock prices update in real-time
- [ ] Dashboard refreshes
- [ ] Alerts trigger in real-time
- [ ] No excessive API calls

### Loading States
- [ ] Skeleton loaders show while loading
- [ ] Spinners appear for async actions
- [ ] Progress indicators work
- [ ] No blank screens

### Error Handling
- [ ] Network error shows message
- [ ] 404 page displays
- [ ] 500 error handled gracefully
- [ ] Error boundaries catch errors
- [ ] Toast notifications for errors

### Accessibility
- [ ] Keyboard navigation works
- [ ] Tab order logical
- [ ] Focus indicators visible
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Alt text on images

---

## 12. Dark Mode / Theming

### Theme Toggle
- [ ] Theme toggle button present
- [ ] Switch to dark mode
- [ ] Colors invert correctly
- [ ] Charts adapt to dark theme
- [ ] All text readable
- [ ] Switch to light mode
- [ ] System preference detection

---

## 13. Advanced Features

### Command Palette
- [ ] Open with Cmd/Ctrl + K
- [ ] Search commands
- [ ] Quick navigation works
- [ ] Actions execute correctly

### Keyboard Shortcuts
- [ ] Shortcuts documented
- [ ] Test common shortcuts
- [ ] No conflicts with browser

### Data Export
- [ ] Export watchlist to CSV
- [ ] Export portfolio to CSV
- [ ] Export screener results
- [ ] Download historical data

### Sharing Features
- [ ] Share watchlist link
- [ ] Share portfolio (if public)
- [ ] Share screener
- [ ] Copy link functionality

---

## 14. Integration Testing

### End-to-End User Journey
- [ ] New user signs up
- [ ] Selects a plan
- [ ] Completes payment
- [ ] Creates watchlist
- [ ] Adds stocks to watchlist
- [ ] Creates screener
- [ ] Sets up alert
- [ ] Alert triggers
- [ ] Exports data
- [ ] Logs out
- [ ] Logs back in - data persists

---

## 15. Browser Compatibility

### Chrome
- [ ] All features work
- [ ] No console errors

### Firefox
- [ ] All features work
- [ ] No console errors

### Safari
- [ ] All features work
- [ ] No console errors

### Edge
- [ ] All features work
- [ ] No console errors

### Mobile Browsers
- [ ] Safari iOS
- [ ] Chrome Android

---

## 16. Security Testing

### XSS Protection
- [ ] Try injecting `<script>alert('XSS')</script>` in inputs
- [ ] Verify input sanitized

### CSRF Protection
- [ ] Forms have CSRF tokens
- [ ] API calls include auth headers

### Authentication Security
- [ ] Password visible toggle works
- [ ] Passwords masked by default
- [ ] Token stored securely
- [ ] Sensitive routes protected

---

## Issues Found

| Issue # | Page/Component | Severity | Description | Status |
|---------|---------------|----------|-------------|--------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## Test Summary

**Total Tests:** ________________
**Passed:** ________________
**Failed:** ________________
**Blocked:** ________________

**Success Rate:** ________%

**Notes:**
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

**Tested by:** ________________
**Date:** ________________
**Signature:** ________________
