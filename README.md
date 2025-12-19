# TradeScanPro - Stock Scanner Platform

## Overview

TradeScanPro is a professional stock scanning and analysis platform for NASDAQ stocks. It provides real-time data, technical indicators, backtesting capabilities, and customizable charts.

### Core Features
- Real-time stock data scanning
- Advanced technical indicators
- Backtesting engine
- Customizable Stooq HTML5 charts
- Watchlists and favorites
- Price alerts
- Partner referral system
- Subscription billing (PayPal)

### Technology Stack
- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: React, Tailwind CSS
- **Database**: PostgreSQL / MySQL
- **Cache**: Redis (optional)
- **Charts**: Stooq HTML5
- **Payments**: PayPal
- **Deployment**: Cloudflare Tunnel

## Quick Links

- **Setup Guide**: See [SETUP.md](SETUP.md)
- **Features**: See [FEATURES.md](FEATURES.md)
- **Contact**: carter.kiefer2010@outlook.com

## Project Structure

```
stock-scanner-complete/
├── backend/               # Django API backend
│   ├── stocks/           # Main app (stock data, alerts, portfolios)
│   ├── billing/          # PayPal payment integration
│   ├── education/        # Learning content
│   ├── historical_data_scanner.py  # Historical data collection
│   ├── realtime_scanner_ultra_fast.py  # Real-time scanning
│   └── manage.py         # Django management
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── api/         # API clients
│   │   └── hooks/       # Custom hooks
│   └── public/          # Static assets
└── docs/                # Additional documentation
```

## Key Components

### Backend Services
1. **Historical Data Scanner**: Collects historical price data with 12-hour spread delays to avoid rate limits
2. **Real-time Scanner**: Ultra-fast real-time data collection using proxies and caching
3. **REST API**: Comprehensive API for all stock data operations
4. **Billing System**: PayPal integration with subscription management
5. **Referral Analytics**: Complete partner tracking and analytics

### Frontend Applications
1. **Stock Scanner**: Main scanning interface with filters
2. **Chart System**: Stooq HTML5 charts with full customization
3. **Backtesting**: Historical strategy testing
4. **Portfolio Tracker**: Track investments and performance
5. **Education**: Learning materials for traders

## Production Deployment

The platform is deployed using:
- Backend API: `api.tradescanpro.com`
- Frontend: `tradescanpro.com`
- Cloudflare Tunnel for secure API access

## Security

- API-only backend (no HTML templates)
- HTTPS required
- PayPal webhook signature verification
- Rate limiting on critical endpoints
- reCAPTCHA support
- CSRF protection

## Performance

- **Real-time Scanner**: Processes stocks in batches with proxy rotation
- **Historical Scanner**: 12-hour spread delays prevent API throttling
- **Caching**: Redis caching for frequently accessed data
- **Database**: Optimized queries with indexing

## Support

For issues or questions:
- Email: carter.kiefer2010@outlook.com
- GitHub: [Issues](https://github.com/anthropics/claude-code/issues)

## License

Proprietary - All rights reserved
