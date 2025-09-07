# Rate Limiting Guide

## Overview

The Stock Scanner API implements intelligent rate limiting to ensure fair usage while allowing unlimited access to health checks and non-stock-data endpoints for all users.

## Rate Limits by User Type

### Free Users (Anonymous)
- **Stock Data Endpoints**: 100 requests per hour
- **Health & Status Endpoints**: Unlimited
- **Documentation Endpoints**: Unlimited

### Authenticated Users
- **Stock Data Endpoints**: 1,000 requests per hour
- **All Other Endpoints**: Unlimited

### Premium Users
- **All Endpoints**: Unlimited access
- Premium groups: `premium`, `pro`, `enterprise`

### API Key Authentication
- **All Endpoints**: Unlimited access
- Used for backend-to-backend communication (e.g., WordPress integration)

## Endpoints Classification

### Free Endpoints (No Rate Limiting)
These endpoints are always free and have no rate limiting:

- `/health/` - Basic health check
- `/api/health/` - API health check
- `/health/detailed/` - Detailed system health
- `/health/ready/` - Readiness probe
- `/health/live/` - Liveness probe
- `/docs/` - API documentation
- `/api/docs/` - API documentation (alternative)
- `/endpoint-status/` - Endpoint status check
- `/api/endpoint-status/` - API endpoint status
- `/` - Homepage
- `/api/` - API root
- `/accounts/*` - Authentication endpoints
- `/admin/` - Admin panel (requires authentication)
- `/static/*` - Static files
- `/media/*` - Media files

### Rate-Limited Endpoints
These endpoints are subject to rate limiting for free users:

- `/api/stocks/` - Stock listings
- `/api/stock/*` - Individual stock data
- `/api/search/` - Stock search
- `/api/trending/` - Trending stocks
- `/api/realtime/*` - Real-time stock data
- `/api/filter/` - Stock filtering
- `/api/market-stats/` - Market statistics
- `/api/portfolio/*` - Portfolio management
- `/api/watchlist/*` - Watchlist management
- `/api/alerts/*` - Stock alerts
- `/revenue/*` - Revenue analytics

## Rate Limit Headers

When making requests to rate-limited endpoints, the following headers are included in responses:

- `X-RateLimit-Limit`: Maximum requests allowed in the window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets
- `Retry-After`: Seconds to wait before retrying (only on 429 responses)

## Rate Limit Response

When rate limit is exceeded, the API returns:

```json
{
    "error": "Rate limit exceeded",
    "message": "You have exceeded the rate limit of 100 requests per hour.",
    "retry_after": 3600,
    "limit": 100,
    "window": 3600,
    "upgrade_message": "Upgrade to a premium account for higher limits or unlimited access."
}
```

HTTP Status Code: `429 Too Many Requests`

## Configuration

Rate limits can be configured via environment variables:

- `RATE_LIMIT_FREE_USERS`: Requests per hour for free users (default: 100)
- `RATE_LIMIT_AUTHENTICATED_USERS`: Requests per hour for authenticated users (default: 1000)
- `RATE_LIMIT_WINDOW`: Window size in seconds (default: 3600)

## API Key Authentication

For backend services and integrations, use API key authentication to bypass rate limiting:

```bash
curl -H "X-API-Key: your-api-key" https://api.retailtradescanner.com/api/stocks/
```

Set the API key in the environment:
```bash
WORDPRESS_API_KEY=your-secure-api-key
```

## Testing Rate Limits

### Using the Management Command
```bash
python manage.py test_rate_limits
python manage.py test_rate_limits --clear-cache
```

### Using the Test Script
```bash
python test_rate_limiting.py
```

### Manual Testing with curl
```bash
# Test free endpoint (no rate limiting)
for i in {1..20}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health/; done

# Test rate-limited endpoint
for i in {1..150}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/stocks/; done
```

## Best Practices

1. **Cache responses** when possible to reduce API calls
2. **Use batch endpoints** when available to get multiple resources in one request
3. **Implement exponential backoff** when receiving 429 responses
4. **Monitor rate limit headers** to track usage
5. **Use API key authentication** for backend services
6. **Upgrade to premium** for production applications requiring higher limits

## Troubleshooting

### Issue: Getting rate limited on health endpoints
- Health endpoints should never be rate limited
- Check that the endpoint path matches the free endpoint list exactly
- Verify the middleware is properly configured in settings.py

### Issue: API key not working
- Ensure the `X-API-Key` header is set correctly
- Verify the API key matches the `WORDPRESS_API_KEY` environment variable
- Check that `APIKeyAuthenticationMiddleware` is in the middleware stack

### Issue: Premium users getting rate limited
- Verify the user is in one of the premium groups
- Check that authentication is working properly
- Ensure the middleware can access user group information

## Support

For questions about rate limiting or to request higher limits, please contact support.