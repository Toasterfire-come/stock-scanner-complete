# 🚀 Production Deployment Guide - Stock Scanner Pro

## 🔒 Security-Enhanced React Frontend

This guide covers deploying the React frontend to a static hosting environment with enterprise-grade security features.

## 📋 Pre-Deployment Checklist

### ✅ Environment Configuration
- [ ] Update `/app/frontend/.env.production` with production values
- [ ] Verify `REACT_APP_BACKEND_URL` points to your Django backend
- [ ] Confirm `REACT_APP_API_PASSWORD` matches your backend credentials
- [ ] Set up PayPal production client ID

### ✅ Security Features Enabled
- [x] Input validation and sanitization (DOMPurify)
- [x] Rate limiting (60 requests/minute by default)
- [x] Session management with timeout
- [x] CSRF protection
- [x] XSS protection
- [x] Content Security Policy (CSP)
- [x] Secure token storage
- [x] Request queuing and concurrent request limiting
- [x] Error sanitization in production
- [x] Security headers
- [x] Console logging disabled in production

## 🏗️ Build Process

### 1. Production Build
```bash
cd /app/frontend

# Set production environment variables
export NODE_ENV=production
export REACT_APP_BACKEND_URL=https://api.retailtradescanner.com
export REACT_APP_API_PASSWORD="((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop"

# Run production build
npm run build:production
```

### 2. Deployment Readiness Check
```bash
npm run deploy:check
```

## 🌐 Static Hosting Options

### Option 1: Netlify (Recommended)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy to Netlify
netlify deploy --prod --dir=build
```

**Netlify Configuration (`netlify.toml`):**
```toml
[build]
  publish = "build"
  command = "npm run build:production"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Strict-Transport-Security = "max-age=31536000; includeSubDomains"

[[headers]]
  for = "*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Option 2: Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel --prod
```

**Vercel Configuration (`vercel.json`):**
```json
{
  "buildCommand": "npm run build:production",
  "outputDirectory": "build",
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html",
      "headers": {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' https://www.paypal.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://api.retailtradescanner.com https://www.paypal.com; frame-src https://www.paypal.com; object-src 'none'; base-uri 'self'"
      }
    }
  ]
}
```

### Option 3: AWS S3 + CloudFront
```bash
# Build the application
npm run build:production

# Upload to S3 (replace with your bucket)
aws s3 sync build/ s3://your-bucket-name --delete

# Configure CloudFront for security headers
```

**CloudFront Lambda@Edge for Security Headers:**
```javascript
exports.handler = (event, context, callback) => {
    const response = event.Records[0].cf.response;
    const headers = response.headers;
    
    headers['x-frame-options'] = [{key: 'X-Frame-Options', value: 'DENY'}];
    headers['x-content-type-options'] = [{key: 'X-Content-Type-Options', value: 'nosniff'}];
    headers['x-xss-protection'] = [{key: 'X-XSS-Protection', value: '1; mode=block'}];
    headers['referrer-policy'] = [{key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin'}];
    headers['strict-transport-security'] = [{key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains'}];
    
    callback(null, response);
};
```

## 🔧 Backend Integration

### Django Backend Requirements
Ensure your Django backend at `https://api.retailtradescanner.com` has:

1. **CORS Configuration:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-client-version',
    'x-client-environment',
]
```

2. **Security Headers:**
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

3. **API Endpoints:** All endpoints with `/api/` prefix as documented

## 🔍 Post-Deployment Testing

### 1. Security Headers Check
```bash
curl -I https://your-domain.com
```

Verify presence of:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`
- `Content-Security-Policy`

### 2. API Connectivity Test
```bash
# Test from your deployed frontend
curl -H "Origin: https://your-domain.com" https://api.retailtradescanner.com/api/health/
```

### 3. Performance Testing
- Test page load speed (should be < 3 seconds)
- Verify service worker caching
- Check mobile responsiveness
- Test offline functionality

## 🚨 Security Monitoring

### 1. Content Security Policy Violations
Monitor CSP violations in your browser console and backend logs.

### 2. Rate Limiting
The frontend enforces client-side rate limiting:
- 60 requests per minute per user
- 5 concurrent requests maximum
- Exponential backoff on failures

### 3. Session Management
- Sessions expire after 30 minutes of inactivity
- Automatic token refresh 5 minutes before expiry
- Secure token storage with encryption

## 🔧 Environment Variables Reference

### Production Environment (`.env.production`)
```bash
# Backend Configuration
REACT_APP_BACKEND_URL=https://api.retailtradescanner.com
REACT_APP_API_PASSWORD=((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop

# PayPal Production
REACT_APP_PAYPAL_CLIENT_ID=your-production-paypal-client-id
REACT_APP_PAYPAL_MODE=live

# Security
REACT_APP_ENABLE_DEVTOOLS=false
REACT_APP_ENABLE_CONSOLE_LOGS=false
REACT_APP_DISABLE_RIGHT_CLICK=true

# Performance
REACT_APP_MAX_API_CALLS_PER_MINUTE=60
REACT_APP_MAX_CONCURRENT_REQUESTS=5
REACT_APP_SESSION_TIMEOUT_MINUTES=30

# Analytics
REACT_APP_GA_TRACKING_ID=your-production-google-analytics-id
```

## 📊 Performance Optimization

### Built-in Optimizations
- [x] Code splitting with React.lazy()
- [x] Service worker for caching
- [x] Gzip compression (configured in hosting)
- [x] Image optimization
- [x] CSS minification
- [x] JavaScript minification
- [x] Source maps disabled in production

### Monitoring
```bash
# Analyze bundle size
npm run analyze

# Security audit
npm run security:audit
```

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors:** Verify backend CORS configuration includes your frontend domain
2. **CSP Violations:** Check browser console for blocked resources
3. **Rate Limiting:** Increase limits if needed for your use case
4. **Session Timeouts:** Adjust session timeout in environment variables

### Debug Mode
For debugging in production (temporary):
```bash
REACT_APP_ENABLE_CONSOLE_LOGS=true
REACT_APP_ENABLE_DEBUG=true
```

## 📞 Support

For deployment issues:
1. Check the deployment readiness checklist
2. Verify all environment variables are set
3. Test API connectivity from your hosting environment
4. Review browser console for security errors

## 🎯 Performance Targets

- **First Contentful Paint:** < 1.5s
- **Largest Contentful Paint:** < 2.5s
- **Cumulative Layout Shift:** < 0.1
- **First Input Delay:** < 100ms
- **Security Score:** A+ on Mozilla Observatory

---

**🔒 Your React frontend is now production-ready with enterprise-grade security features!**