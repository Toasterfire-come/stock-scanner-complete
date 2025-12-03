# Deployment Instructions: MIME Type Fixes

## Problem Summary
The production site (tradescanpro.com) is serving CSS and JS files with incorrect MIME types:
- CSS files return `content-type: text/html` instead of `text/css`
- JS files return `content-type: text/html` instead of `application/javascript`
- This causes browsers to refuse loading these resources

## What Was Fixed

### 1. `.htaccess` (frontend/public/.htaccess)
- Added explicit MIME type declarations for all static file types
- Added rules to prevent static files from being rewritten to index.html
- Maintained all existing security headers and caching rules

### 2. `index.html` (frontend/public/index.html)
- Fixed duplicate hero.avif preload declarations
- Added proper `type` attributes to image preloads
- Added CSS preload optimization
- Used correct API URL (api.tradescanpro.com)

### 3. Build Output
- Successfully built with all fixes in `/frontend/build/`
- Build size: ~3.1MB
- Ready for deployment

## Deployment Options

### Option 1: Merge to Main and Deploy (RECOMMENDED)
```bash
# 1. Switch to main branch
git checkout main

# 2. Merge the fix branch
git merge claude/fix-mime-type-errors-011CUtjH3WoE449ub6H9iyHv

# 3. Push to main
git push origin main

# 4. Deploy using existing deployment script
cd frontend
PUPPETEER_SKIP_DOWNLOAD=true npm install
DISABLE_ESLINT_PLUGIN=true npm run build

# 5. Use your SFTP client or run deploy script from a machine with network access
```

### Option 2: Deploy from Current Build
The current build in `/frontend/build/` contains all the fixes and is ready to deploy.

```bash
# Upload the entire /frontend/build/ directory to your web server root
# Make sure to preserve the .htaccess file!

# Via SFTP (from a machine with network access):
cd /home/user/stock-scanner-complete
./deploy.sh

# Or use your preferred SFTP client:
# Host: access-5018544625.webspace-host.com
# User: a1531117
# Port: 22
# Upload: /frontend/build/* to server root (/)
```

### Option 3: Manual File Updates
If you only want to update the critical files:

```bash
# Upload these key files to your server:
1. /frontend/build/.htaccess → Server root/.htaccess
2. /frontend/build/index.html → Server root/index.html
3. /frontend/build/static/css/* → Server root/static/css/
4. /frontend/build/static/js/* → Server root/static/js/
```

## Testing After Deployment

Run the included test script:
```bash
./test-mime-types.sh
```

Or test manually:
```bash
# Test CSS MIME type (should show: content-type: text/css)
curl -sI https://tradescanpro.com/static/css/main.d5fc19a7.css | grep content-type

# Test JS MIME type (should show: content-type: application/javascript)
curl -sI https://tradescanpro.com/static/js/main.6b8c4a87.js | grep content-type

# Test AVIF image (should show: content-type: image/avif)
curl -sI https://tradescanpro.com/hero.avif | grep content-type
```

### Expected Results
✅ CSS files: `content-type: text/css`
✅ JS files: `content-type: application/javascript`
✅ AVIF images: `content-type: image/avif`
✅ WebP images: `content-type: image/webp`
✅ Security headers present (HSTS, X-Content-Type-Options)

### Browser Console Test
After deployment, open https://tradescanpro.com in a browser:
1. Open Developer Tools (F12)
2. Go to Console tab
3. Refresh the page (Ctrl+Shift+R for hard refresh)
4. **Should NOT see any errors about:**
   - "Refused to apply style from..."
   - "Refused to execute script from..."
   - "MIME type ('text/html') is not a supported stylesheet MIME type"

## Key Pages to Test

After deployment, verify these pages load correctly:
- https://tradescanpro.com/ (Home)
- https://tradescanpro.com/scanner (Scanner)
- https://tradescanpro.com/screener (Screener)
- https://tradescanpro.com/portfolio (Portfolio)
- https://tradescanpro.com/alerts (Alerts)
- https://tradescanpro.com/pricing (Pricing)
- https://tradescanpro.com/about (About)

## Troubleshooting

### If MIME types are still wrong after deployment:

1. **Verify .htaccess was uploaded**
   - Check that .htaccess exists in your server root
   - Verify it contains the MIME type declarations

2. **Check Apache configuration**
   - Ensure `mod_mime` is enabled
   - Ensure `.htaccess` files are allowed (AllowOverride All)

3. **Clear cache**
   - Clear browser cache (Ctrl+Shift+Delete)
   - Clear server cache if applicable
   - May need to restart Apache: `sudo systemctl restart apache2`

4. **Check file permissions**
   - .htaccess should be readable: `chmod 644 .htaccess`

5. **Test directly**
   ```bash
   # Get the actual content-type header
   curl -sI https://tradescanpro.com/static/css/main.d5fc19a7.css
   ```

## Important Notes

- The deployment script in `deploy.sh` switches to main branch before deploying
- Make sure to merge your fixes to main OR modify the deployment script
- Keep backups before deploying
- The fixed .htaccess maintains all existing security settings

## Branch Information
- Fix Branch: `claude/fix-mime-type-errors-011CUtjH3WoE449ub6H9iyHv`
- Commits: 2 commits with MIME fixes and merge resolution
- Status: Ready for merge to main
