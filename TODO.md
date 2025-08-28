# Theme TODO (Client Additions) – Status

- [x] Session countdown pill in header showing remaining time
- [x] 12-hour browser-side idle auto-logout with per-second countdown
- [x] 2-minute warning modal with “Stay signed in” and “Sign out now”
- [x] Plan badge fetch only on sign-in; cache in localStorage per user
- [x] Hidden “Refresh Plan” link (revealed while holding Alt) to refetch plan and update cache on demand
- [x] Session policy popover in header describing current idle policy
- [x] Session data popover listing key cookies and cache markers (wordpress_logged_in, ssc_login_user, ssc_last_activity, ssc_plan, localStorage plan)
- [x] Clear session data action to remove plan cache and activity cookies
- [x] Smooth dropdown + optional mega-menu with click/keyboard/outside-click handling
- [x] Market status chip (Open/Closed)
- [x] Smooth scrolling, in-view animations, copy-to-clipboard for symbols

## Admin/Server-side (lightweight)
- [x] Admin-configurable idle policy (enable/disable + hours) under Appearance → Stock Scanner
- [x] Plan badge fetched server-side via admin-ajax -> {api_base}/billing/current-plan using plugin settings (URL + Secret)
- [x] Admin-only health checker (Backend Offline page) calling {api_base}/health via server-side AJAX

All items are implemented in this theme. Configure plugin options for API URL/Secret and set Theme Options as desired.