# Trade Scan Pro

Stock scanning + watchlists/portfolios + AI backtesting.

## Quick start

- **Install / run**: see `docs/INSTALL.md`

## Repo layout

- **Backend**: `backend/` (Django + REST)
- **Frontend**: `frontend/` (React + Tailwind)

## Notes

- **Backtesting executes generated code** (restricted + timeouts). For production, isolate execution in a worker/container.

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

## License

Proprietary (see repository owner).
