# Stock Scanner Pro WordPress Theme

A professional WordPress theme for stock market analysis and portfolio management, integrated with Django backend API.

## Features

### 🎨 Design
- Modern, clean interface with dark/light mode support
- Responsive design that works on all devices  
- Professional color scheme optimized for financial data
- Accessibility compliant (WCAG 2.1)

### 📊 Stock Market Integration
- Real-time stock data via Django API
- Interactive charts with Chart.js
- Market heatmaps and trend analysis
- Stock search and lookup functionality
- Portfolio and watchlist management
- Price alerts and notifications

### 🔧 Technical Features
- Django REST API integration
- WordPress custom post types for market data
- Advanced caching system for performance
- SEO optimized structure
- Security hardened with best practices
- Progressive Web App (PWA) ready

### 📱 Pages Included
- Dashboard (user overview)
- Market Overview (market statistics and charts)
- Stock Lookup (search and analyze stocks)
- Portfolio Management
- Watchlist Management
- Stock News Feed
- User Settings
- Billing and Subscription pages
- Authentication pages
- Legal pages (Privacy, Terms, etc.)

## Installation

1. **Upload Theme**
   ```bash
   # Upload the theme to your WordPress themes directory
   wp-content/themes/stock-scanner-pro-theme/
   ```

2. **Activate Theme**
   - Go to WordPress Admin > Appearance > Themes
   - Find "Stock Scanner Pro" and click "Activate"

3. **Configure API Settings**
   - Go to Appearance > Theme Options
   - Enter your Django API URL (e.g., `http://localhost:8000/api`)
   - Add API authentication key if required
   - Set cache timeout (recommended: 300 seconds)

4. **Setup Menus**
   - Go to Appearance > Menus
   - Create menus for "Primary Navigation", "Dashboard Navigation", and "Footer Navigation"
   - Assign menu locations

5. **Install Required Plugins** (Optional)
   - WordPress SEO plugin for better SEO
   - Caching plugin for performance
   - Security plugin for enhanced protection

## Configuration

### API Integration
The theme connects to a Django backend API for stock data. Configure the connection in:
- **Appearance > Theme Options**
- **Functions.php** (for developers)

### Environment Variables
Set these in your `wp-config.php` or theme options:
```php
define('STOCK_SCANNER_API_URL', 'http://localhost:8000/api');
define('STOCK_SCANNER_API_KEY', 'your-api-key');
define('STOCK_SCANNER_CACHE_TIMEOUT', 300);
```

### Menu Locations
- **Primary Navigation**: Main site navigation in header
- **Dashboard Navigation**: Side navigation for dashboard pages  
- **Footer Navigation**: Links in footer area

### Widget Areas
- **Sidebar**: Standard sidebar widgets
- **Dashboard Sidebar**: Widgets for dashboard pages
- **Footer Widgets**: Footer widget areas

## Customization

### Custom CSS
Add custom styles in:
- **Appearance > Customize > Additional CSS**
- **Child theme** (recommended for major changes)

### Color Scheme
The theme uses CSS custom properties for easy color customization:
```css
:root {
  --color-primary-500: #3b82f6;
  --color-success-500: #10b981;
  --color-danger-500: #ef4444;
  /* ... more colors */
}
```

### Typography
Default fonts:
- **UI Text**: Inter (Google Fonts)
- **Numbers/Code**: JetBrains Mono (Google Fonts)

### JavaScript Customization
Main JavaScript files:
- `assets/js/main.js` - Core functionality
- `assets/js/api.js` - API integration
- `assets/js/dashboard.js` - Dashboard features
- `assets/js/charts.js` - Chart functionality

## API Integration

### Required Endpoints
The theme expects these API endpoints from the Django backend:

```bash
GET /api/stocks/                    # List stocks with filtering
GET /api/stock/{ticker}/           # Individual stock details
GET /api/search/?q={query}         # Stock search
GET /api/trending/                 # Trending stocks
GET /api/market-stats/             # Market overview
GET /api/portfolio/                # User portfolio
GET /api/watchlist/                # User watchlist
GET /api/news/                     # Market news
POST /api/alerts/create/           # Create price alert
POST /api/subscription/            # Email subscription
```

### Authentication
The theme supports:
- WordPress session-based authentication
- API token authentication
- Custom authentication methods

### Data Caching
- WordPress transients API for caching
- Configurable cache timeouts
- Manual cache clearing functionality

## Page Templates

### Dashboard Template
**File**: `page-templates/page-dashboard.php`
**Features**:
- Portfolio summary
- Watchlist preview
- Market overview
- News feed
- Quick actions

### Market Overview Template
**File**: `page-templates/page-market-overview.php`
**Features**:
- Market statistics
- Interactive charts
- Market heatmap
- Sector performance
- Top performers lists

### Stock Lookup Template
**File**: `page-templates/page-stock-lookup.php`
**Features**:
- Stock search with autocomplete
- Detailed stock information
- Price charts
- Trading statistics
- Related news

## Performance Optimization

### Caching Strategy
- API responses cached for 5 minutes
- Transients used for expensive operations
- CSS/JS minification in production
- Image optimization recommended

### Loading Optimization
- Critical CSS inlined
- Non-critical JavaScript deferred
- Progressive image loading
- Lazy loading for off-screen content

### Database Queries
- Optimized WordPress queries
- Minimal database calls
- Efficient caching patterns

## Security Features

### Built-in Security
- XSS protection with sanitized outputs
- CSRF protection with nonces
- SQL injection prevention
- Content Security Policy headers
- Rate limiting on API requests

### User Data Protection
- Encrypted sensitive data storage
- Secure session handling
- Privacy-compliant user tracking
- GDPR-ready data handling

## Browser Support

### Supported Browsers
- Chrome 90+ ✅
- Firefox 90+ ✅
- Safari 14+ ✅
- Edge 90+ ✅
- Mobile browsers ✅

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features with JavaScript enabled
- Fallbacks for older browsers

## Development

### File Structure
```
stock-scanner-pro-theme/
├── assets/
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files
│   ├── images/       # Theme images
│   └── fonts/        # Custom fonts
├── includes/         # PHP includes
├── page-templates/   # Custom page templates
├── functions.php     # Theme functions
├── style.css         # Main stylesheet with theme header
├── index.php         # Main template
├── header.php        # Header template
├── footer.php        # Footer template
└── README.md         # This file
```

### Development Commands
```bash
# Install dependencies (if using build tools)
npm install

# Watch for changes during development  
npm run watch

# Build for production
npm run build

# Lint CSS and JavaScript
npm run lint
```

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with proper testing
4. Submit pull request with description

## Troubleshooting

### Common Issues

**API Connection Failed**
- Check API URL in theme options
- Verify Django backend is running
- Check API key if authentication required
- Review browser console for errors

**Charts Not Loading**
- Verify Chart.js is loading properly
- Check for JavaScript errors in console
- Ensure canvas elements exist on page
- Verify data format from API

**Styling Issues**
- Clear browser cache
- Check CSS file loading
- Verify no plugin conflicts
- Test with default WordPress theme

**Performance Issues**
- Enable caching plugin
- Optimize images
- Check API response times
- Review database queries

### Debug Mode
Enable WordPress debug mode for development:
```php
// In wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

### Support
For technical support:
- Check documentation first
- Review GitHub issues
- Contact theme developer
- WordPress community forums

## Changelog

### Version 1.0.0
- Initial release
- Full Django API integration
- Responsive design implementation
- Dashboard and market overview pages
- Stock lookup functionality
- Security hardening
- Performance optimizations

## License

This theme is released under the GPL v2 or later license.

## Credits

- **Chart.js** - Chart and graph library
- **Font Awesome** - Icon library  
- **Google Fonts** - Typography (Inter, JetBrains Mono)
- **WordPress** - Content management system
- **Django** - Backend API framework

---

**Stock Scanner Pro Theme** - Professional WordPress theme for stock market applications.