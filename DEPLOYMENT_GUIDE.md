# Production Deployment Guide for Stock Scanner

## 🎯 Overview
This guide provides complete instructions for deploying the Stock Scanner application to production. The system consists of:
- **Frontend**: React SPA deployed to static web hosting
- **Backend**: Django API at https://api.retailtradescanner.com (already deployed)

## ✅ Pre-Deployment Checklist

### Required Services
- [ ] Static web hosting (Netlify, Vercel, AWS S3 + CloudFront, etc.)
- [ ] Domain name configured with DNS
- [ ] SSL certificate (usually auto-provided by hosting service)
- [ ] CDN for static assets (optional but recommended)
- [ ] Error tracking service (Sentry, LogRocket)
- [ ] Analytics (Google Analytics, Mixpanel)

### Environment Variables
```bash
# Frontend (.env.production)
REACT_APP_ENV=production
REACT_APP_API_URL=https://api.retailtradescanner.com
REACT_APP_API_KEY=((#cx+mb@f-(8x*p@9mfnanqe%ha1@6-b%w)q##v@)lanop
REACT_APP_WEBSITE_URL=https://yourdomai.com
GENERATE_SOURCEMAP=false
```

## 🚀 Build Process

### 1. Run Production Build
```bash
# Make build script executable
chmod +x build-production.sh

# Run the build
./build-production.sh
```

This will:
- Install dependencies
- Run tests
- Create optimized production build
- Add security headers
- Generate deployment package

### 2. Manual Build (Alternative)
```bash
cd frontend
npm ci
npm run build:prod
```

## 📦 Deployment Options

### Option 1: Netlify (Recommended for simplicity)

1. **Via CLI**:
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod --dir=build
```

2. **Via GitHub**:
- Connect repository to Netlify
- Set build command: `npm run build`
- Set publish directory: `build`
- Add environment variables in Netlify dashboard

3. **Add _redirects file** for SPA routing:
```bash
echo "/*    /index.html   200" > frontend/build/_redirects
```

### Option 2: Vercel

```bash
npm install -g vercel
cd frontend
vercel --prod
```

Configuration (`vercel.json`):
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

### Option 3: AWS S3 + CloudFront

1. **Create S3 bucket**:
```bash
aws s3 mb s3://stockscanner-frontend
aws s3 website s3://stockscanner-frontend --index-document index.html --error-document index.html
```

2. **Upload build**:
```bash
aws s3 sync frontend/build/ s3://stockscanner-frontend --delete
```

3. **Configure CloudFront**:
- Create distribution pointing to S3 bucket
- Set custom error pages to redirect to index.html
- Configure caching behaviors
- Add security headers via Lambda@Edge

### Option 4: Traditional Web Server (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomai.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.retailtradescanner.com;" always;

    root /var/www/stockscanner;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        try_files $uri /index.html;
    }
}
```

## 🔒 Security Configuration

### 1. Content Security Policy
Already configured in the build. Additional headers can be added at the hosting level.

### 2. CORS Configuration
The Django backend at api.retailtradescanner.com handles CORS. Ensure your domain is whitelisted.

### 3. API Key Security
- Never expose API keys in client-side code
- Use environment variables
- Implement rate limiting

## 🎯 Post-Deployment Verification

### 1. Functional Testing
```bash
# Check API connectivity
curl https://api.retailtradescanner.com/health/

# Test authentication
curl -X POST https://api.retailtradescanner.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### 2. Performance Testing
- Run Lighthouse audit
- Check bundle size (should be < 500KB gzipped)
- Test loading times (target < 3s on 3G)

### 3. Security Scan
```bash
# Check security headers
curl -I https://yourdomai.com

# Run SSL test
# Visit: https://www.ssllabs.com/ssltest/
```

## 📊 Monitoring Setup

### 1. Error Tracking (Sentry)
```javascript
// Add to index.js
import * as Sentry from "@sentry/react";

if (process.env.REACT_APP_ENV === 'production') {
  Sentry.init({
    dsn: "YOUR_SENTRY_DSN",
    environment: "production",
    tracesSampleRate: 0.1,
  });
}
```

### 2. Analytics (Google Analytics)
```html
<!-- Add to public/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### 3. Uptime Monitoring
- Configure UptimeRobot or Pingdom
- Monitor both frontend and API endpoints
- Set up alerts for downtime

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
        
    - name: Build
      run: |
        cd frontend
        npm run build:prod
      env:
        REACT_APP_API_URL: ${{ secrets.API_URL }}
        REACT_APP_API_KEY: ${{ secrets.API_KEY }}
        
    - name: Deploy to Netlify
      uses: netlify/actions/cli@master
      with:
        args: deploy --prod --dir=frontend/build
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## 🚨 Rollback Procedure

### Quick Rollback
1. **Netlify/Vercel**: Use dashboard to rollback to previous deployment
2. **S3/CloudFront**: Keep previous build, swap S3 objects
3. **Nginx**: Keep previous build directory, update symlink

### Rollback Script
```bash
#!/bin/bash
# rollback.sh

CURRENT_LINK="/var/www/stockscanner/current"
PREVIOUS_BUILD=$(readlink $CURRENT_LINK | sed 's/releases\///' | awk '{print $1-1}')

ln -sfn /var/www/stockscanner/releases/$PREVIOUS_BUILD $CURRENT_LINK
nginx -s reload

echo "Rolled back to build $PREVIOUS_BUILD"
```

## 📈 Performance Optimization

### 1. Enable Compression
- Gzip/Brotli for text assets
- Image optimization (WebP format)
- Lazy loading for images

### 2. Caching Strategy
```
# Static assets (1 year)
/static/* - Cache-Control: public, max-age=31536000, immutable

# HTML (no cache)
/index.html - Cache-Control: no-cache, no-store, must-revalidate

# API responses (varies)
/api/* - Cache-Control: private, max-age=0
```

### 3. CDN Configuration
- Use CloudFlare, Fastly, or AWS CloudFront
- Configure edge locations
- Set up custom caching rules

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check API allows your domain
   - Verify credentials are included
   - Check preflight requests

2. **404 on Refresh**
   - Configure SPA routing on server
   - Add fallback to index.html

3. **API Connection Failed**
   - Verify API URL in environment
   - Check API health endpoint
   - Verify API key is correct

4. **Slow Performance**
   - Check bundle size
   - Enable compression
   - Optimize images
   - Use CDN

## 📝 Maintenance

### Regular Tasks
- [ ] Weekly: Check error logs
- [ ] Monthly: Review analytics
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Yearly: SSL certificate renewal

### Monitoring Dashboard
Create a dashboard with:
- API health status
- Error rate
- Response times
- User activity
- Revenue metrics

## 🎉 Launch Checklist

### Pre-Launch
- [ ] All tests passing
- [ ] Security scan complete
- [ ] Performance benchmarks met
- [ ] Backup plan ready
- [ ] Support team briefed

### Launch Day
- [ ] Deploy to production
- [ ] Verify all endpoints
- [ ] Test critical user flows
- [ ] Monitor error rates
- [ ] Check performance metrics

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Gather user feedback
- [ ] Address critical issues
- [ ] Plan improvements
- [ ] Celebrate! 🎊

## 📞 Support Contacts

- **API Issues**: api.retailtradescanner.com/support
- **Hosting Issues**: [Your hosting provider support]
- **Domain/DNS**: [Your registrar support]
- **Payment Issues**: Stripe support

## 🔗 Useful Links

- [Django Backend Repo](https://github.com/Toasterfire-come/stock-scanner-complete)
- [React Documentation](https://reactjs.org/docs)
- [Django Documentation](https://docs.djangoproject.com)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)

---

**Remember**: Always test in a staging environment before deploying to production!