// Centralized documentation content map for dynamic docs rendering
// Each article is defined under a category with a slug

export const categoriesMeta = {
  'getting-started': {
    title: 'Getting Started',
    description: 'Learn the basics of using Trade Scan Pro',
    badgeColor: 'bg-green-100 text-green-800',
    icon: 'BookOpen',
  },
  'stock-screening': {
    title: 'Stock Screening',
    description: 'Master our advanced screening tools',
    badgeColor: 'bg-blue-100 text-blue-800',
    icon: 'BarChart3',
  },
  'alerts': {
    title: 'Alerts & Notifications',
    description: 'Set up and manage your alerts',
    badgeColor: 'bg-orange-100 text-orange-800',
    icon: 'Bell',
  },
  'portfolio': {
    title: 'Portfolio Management',
    description: 'Track and analyze your investments',
    badgeColor: 'bg-purple-100 text-purple-800',
    icon: 'DollarSign',
  },
  'watchlists': {
    title: 'Watchlists',
    description: 'Organize and monitor your stocks',
    badgeColor: 'bg-yellow-100 text-yellow-800',
    icon: 'Eye',
  },
  'api': {
    title: 'API & Integrations',
    description: 'Connect Trade Scan Pro with other tools',
    badgeColor: 'bg-gray-100 text-gray-800',
    icon: 'Code',
  },
};

export const docsContent = {
  'getting-started': {
    'read-data': {
      title: 'How to Read Stock Data',
      description: 'Understand technical and fundamental data in our platform.',
      readTime: '6 min',
      updated: 'Updated Dec 2024',
      icon: 'TrendingUp',
      sections: [
        {
          title: 'Price & Volume Basics',
          text: 'Core market data visible across charts, tables, and detail views.',
          bullets: [
            'Last Price and Change: Current trading price and intraday change',
            'Bid/Ask: Best current buy/sell offers and spread tightness',
            'Volume: Shares traded today vs. average volume',
            'OHLC: Open, high, low, close for selected timeframes',
          ],
        },
        {
          title: 'Technical Indicators',
          text: 'Momentum and trend tools to read market behavior.',
          bullets: [
            'Moving Averages: Trend direction and dynamic support/resistance',
            'RSI: Momentum oscillator; <30 oversold, >70 overbought (context-dependent)',
            'MACD: Trend momentum and crossovers for entries/exits',
            'Bollinger Bands: Volatility and mean reversion signals',
          ],
        },
        {
          title: 'Fundamental Metrics',
          text: 'Business health, profitability, and valuation indicators.',
          bullets: [
            'Market Cap: Company size; impacts liquidity and risk profile',
            'P/E and PEG: Valuation vs. earnings and growth expectations',
            'Revenue & EPS Growth: Trajectory and consistency across quarters',
            'Debt Ratios: Leverage risk via Debt/Equity and interest coverage',
          ],
        },
        {
          title: 'Events & News',
          text: 'Catalysts that often precede volatility.',
          bullets: [
            'Earnings Dates: Guidance and surprises drive gaps and trends',
            'Dividends: Ex-dividend dates impact short-term price behavior',
            'News & Filings: Material disclosures, M&A, regulatory updates',
          ],
        },
      ],
      related: [
        { title: 'Understanding Technical Indicators', link: '/docs/stock-screening/technical-indicators' },
        { title: 'Using Fundamental Filters', link: '/docs/stock-screening/fundamental-filters' },
      ],
    },
  },
  'stock-screening': {
    'advanced-techniques': {
      title: 'Advanced Screening Techniques',
      description: 'Combine filters, logical groups, and backtests for precision.',
      readTime: '10 min',
      updated: 'Updated Dec 2024',
      icon: 'Settings',
      sections: [
        {
          title: 'Filter Grouping',
          text: 'Use AND/OR groups to express complex logic.',
          bullets: [
            'Group technical momentum with fundamental quality',
            'Limit universe by liquidity and price ranges first',
            'Use exclusion groups to remove penny stocks or ADRs',
          ],
        },
        {
          title: 'Timeframe Consistency',
          text: 'Align indicators to avoid mixed signals.',
          bullets: [
            'Match moving average lengths to strategy horizon',
            "Confirm weekly trend when screening on daily data",
            'Use multiple timeframes only with clear precedence rules',
          ],
        },
        {
          title: 'Result Calibration',
          text: 'Target 20-50 candidates; refine iteratively.',
          bullets: [
            'Tighten thresholds when results exceed 200',
            'Loosen constraints if fewer than 10 results',
            'Sort by signal strength or custom score',
          ],
        },
      ],
      related: [
        { title: 'Saving and Sharing Screeners', link: '/docs/stock-screening/save-share' },
        { title: 'Technical Indicators', link: '/docs/stock-screening/technical-indicators' },
      ],
    },
    'technical-indicators': {
      title: 'Understanding Technical Indicators',
      description: 'Master RSI, MACD, Bollinger Bands, and moving averages.',
      readTime: '12 min',
      updated: 'Updated Dec 2024',
      icon: 'BarChart3',
      sections: [
        {
          title: 'Trend Indicators',
          text: 'Follow the path of least resistance.',
          bullets: [
            'SMA/EMA: Smoother vs. responsive trends',
            '200-day MA: Long-term bias; above bullish, below cautious',
            'Golden/Death Cross: MA crossovers as regime signals',
          ],
        },
        {
          title: 'Momentum Indicators',
          text: 'Identify acceleration and exhaustion.',
          bullets: [
            'RSI: Divergences often precede reversals',
            'MACD Histogram: Momentum shifts and zero-line crosses',
            'Stochastics: Range-bound setups and signals',
          ],
        },
        {
          title: 'Volatility Indicators',
          text: 'Measure dispersion and compression.',
          bullets: [
            'Bollinger Bands: Squeezes signal upcoming expansion',
            'ATR: Position sizing and stop placement',
          ],
        },
      ],
      related: [
        { title: 'Advanced Screening Techniques', link: '/docs/stock-screening/advanced-techniques' },
      ],
    },
    'fundamental-filters': {
      title: 'Using Fundamental Filters',
      description: 'Screen by valuation, growth, profitability, and quality.',
      readTime: '8 min',
      updated: 'Updated Dec 2024',
      icon: 'Target',
      sections: [
        {
          title: 'Valuation',
          text: 'Relative measures to peers/benchmarks.',
          bullets: [
            'P/E, EV/EBITDA for mature firms',
            'PEG for growth-adjusted valuation',
            'Price-to-Sales for early-stage companies',
          ],
        },
        {
          title: 'Growth & Profitability',
          text: 'Separate consistent growers from cyclicals.',
          bullets: [
            'Revenue and EPS 1Y/3Y CAGR thresholds',
            'Gross and Operating Margins to assess scalability',
            'Free Cash Flow yield for resilience',
          ],
        },
        {
          title: 'Quality & Risk',
          text: 'Focus on balance-sheet strength.',
          bullets: [
            'Debt/Equity and Interest Coverage minimums',
            'Altman Z-score where available',
            'Insider ownership and stability',
          ],
        },
      ],
      related: [
        { title: 'Integration Examples', link: '/docs/api/examples' },
      ],
    },
    'save-share': {
      title: 'Saving and Sharing Screeners',
      description: 'Template saving, permissions, and collaboration tips.',
      readTime: '4 min',
      updated: 'Updated Dec 2024',
      icon: 'Save',
      sections: [
        {
          title: 'Saving Templates',
          text: 'Preserve criteria and sort preferences.',
          bullets: [
            'Name templates descriptively with strategy and timeframe',
            'Version your templates as strategies evolve',
          ],
        },
        {
          title: 'Sharing & Permissions',
          text: 'Collaborate securely with teammates.',
          bullets: [
            'Share read-only vs. editable links',
            'Export to CSV/JSON for external analysis',
          ],
        },
        {
          title: 'Automation',
          text: 'Schedule runs and alerts.',
          bullets: [
            'Set periodic re-runs and notifications',
            'Use webhooks for downstream processing',
          ],
        },
      ],
    },
  },
  'alerts': {
    'price-alerts': {
      title: 'Creating Price Alerts',
      description: 'Get notified when stocks hit your target prices.',
      readTime: '5 min',
      updated: 'Updated Dec 2024',
      icon: 'Bell',
      sections: [
        {
          title: 'Alert Types',
          text: 'Absolute, percentage, and trailing price alerts.',
          bullets: [
            'Above/Below price thresholds',
            'Percent change over period',
            'Trailing distance from high/low',
          ],
        },
        {
          title: 'Delivery Channels',
          text: 'Choose where to receive notifications.',
          bullets: [
            'Email and in-app notifications',
            'Webhook and Slack integrations',
            'Quiet hours and batching options',
          ],
        },
      ],
    },
    'volume-news-alerts': {
      title: 'Volume and News Alerts',
      description: 'Track unusual volume spikes and breaking news.',
      readTime: '6 min',
      updated: 'Updated Dec 2024',
      icon: 'Zap',
      sections: [
        {
          title: 'Volume Signals',
          text: 'Detect accumulation and distribution.',
          bullets: [
            'Relative Volume (RVOL) thresholds',
            'Moving average volume comparisons',
          ],
        },
        {
          title: 'News Sources',
          text: 'Customize signal sensitivity.',
          bullets: [
            'Official filings and earnings wires',
            'Curated RSS and premium feeds when available',
          ],
        },
      ],
    },
    'settings': {
      title: 'Managing Alert Settings',
      description: 'Customize notification preferences and delivery methods.',
      readTime: '4 min',
      updated: 'Updated Dec 2024',
      icon: 'Settings',
      sections: [
        {
          title: 'Frequency & Throttling',
          text: 'Avoid overload while staying informed.',
          bullets: [
            'Minimum intervals between alerts per symbol',
            'Digest summaries vs. immediate notifications',
          ],
        },
        {
          title: 'Escalations',
          text: 'Route critical alerts differently.',
          bullets: [
            'High-priority channels for large price moves',
            'Secondary channels for routine updates',
          ],
        },
      ],
    },
    'history': {
      title: 'Alert History and Tracking',
      description: 'Review past alerts and measure effectiveness.',
      readTime: '3 min',
      updated: 'Updated Dec 2024',
      icon: 'Clock',
      sections: [
        {
          title: 'Alert Log',
          text: 'Search and export historical alerts.',
          bullets: [
            'Filter by symbol, date, and type',
            'Export CSV for auditing and analysis',
          ],
        },
        {
          title: 'Outcome Analysis',
          text: 'Was the alert actionable?',
          bullets: [
            'Price paths post-alert snapshots',
            'Hit rates by alert type',
          ],
        },
      ],
    },
  },
  'portfolio': {
    'add-stocks': {
      title: 'Adding Stocks to Portfolio',
      description: 'Input positions and track performance.',
      readTime: '4 min',
      updated: 'Updated Dec 2024',
      icon: 'PlusCircle',
      sections: [
        {
          title: 'Position Details',
          text: 'Accurate entries improve analytics.',
          bullets: [
            'Purchase date, price, and quantity',
            'Fees and tax-lot method if applicable',
          ],
        },
        {
          title: 'Bulk Imports',
          text: 'Speed up onboarding.',
          bullets: [
            'CSV upload with validation',
            'Broker sync where supported',
          ],
        },
      ],
    },
    'analytics': {
      title: 'Portfolio Analytics Overview',
      description: 'Understand risk metrics and attribution.',
      readTime: '8 min',
      updated: 'Updated Dec 2024',
      icon: 'PieChart',
      sections: [
        {
          title: 'Performance',
          text: 'Returns and benchmarks.',
          bullets: [
            'Time-weighted vs. money-weighted returns',
            'Benchmark comparison and tracking error',
          ],
        },
        {
          title: 'Risk',
          text: 'Volatility and drawdowns.',
          bullets: [
            'Standard deviation and beta',
            'Max drawdown and recovery time',
          ],
        },
      ],
    },
    'performance': {
      title: 'Performance Tracking',
      description: 'Monitor returns, benchmarks, and attribution.',
      readTime: '6 min',
      updated: 'Updated Dec 2024',
      icon: 'TrendingUp',
      sections: [
        {
          title: 'Attribution',
          text: 'Understand what drove performance.',
          bullets: [
            'Sector and factor contributions',
            'Winners/losers and position sizing',
          ],
        },
        {
          title: 'Benchmarking',
          text: 'Pick the right comparison.',
          bullets: [
            'Primary vs. custom blend benchmarks',
            'Rebalance schedules for fair comparisons',
          ],
        },
      ],
    },
    'dividends': {
      title: 'Dividend Monitoring',
      description: 'Track payments and yields.',
      readTime: '5 min',
      updated: 'Updated Dec 2024',
      icon: 'DollarSign',
      sections: [
        {
          title: 'Schedules & Forecasts',
          text: 'Stay ahead of ex-dates.',
          bullets: [
            'Upcoming ex-dividend and payment dates',
            'Projected income by month/quarter',
          ],
        },
        {
          title: 'Yield & Safety',
          text: 'Sustainable income signals.',
          bullets: [
            'Dividend yield, payout ratio, growth streaks',
            'Coverage ratios and cash flow support',
          ],
        },
      ],
    },
  },
  'watchlists': {
    'create': {
      title: 'Creating Custom Watchlists',
      description: 'Organize by themes, sectors, or strategies.',
      readTime: '3 min',
      updated: 'Updated Dec 2024',
      icon: 'ListPlus',
      sections: [
        {
          title: 'Structure',
          text: 'Simple but meaningful lists.',
          bullets: [
            'Theme-based (e.g., AI, Renewables)',
            'Strategy-based (Growth, Dividend, Momentum)',
          ],
        },
        {
          title: 'Inputs',
          text: 'Add symbols efficiently.',
          bullets: [
            'Search, paste CSV, or import from screener results',
            'De-duplication and validation',
          ],
        },
      ],
    },
    'manage': {
      title: 'Adding and Removing Stocks',
      description: 'Manage contents efficiently.',
      readTime: '2 min',
      updated: 'Updated Dec 2024',
      icon: 'Pencil',
      sections: [
        {
          title: 'Bulk Operations',
          text: 'Work smarter with lists.',
          bullets: [
            'Multi-select add/remove',
            'Move symbols between lists',
          ],
        },
        {
          title: 'Sync & Hygiene',
          text: 'Keep lists relevant.',
          bullets: [
            'Auto-remove delisted or inactive symbols',
            'Archive old lists for reference',
          ],
        },
      ],
    },
    'analytics': {
      title: 'Watchlist Analytics',
      description: 'Analyze performance and trends.',
      readTime: '7 min',
      updated: 'Updated Dec 2024',
      icon: 'ChartLine',
      sections: [
        {
          title: 'Overview Metrics',
          text: 'Understand list health quickly.',
          bullets: [
            'Average return and dispersion',
            'Volatility and correlation indicators',
          ],
        },
        {
          title: 'Leaders & Laggards',
          text: 'Focus where it matters.',
          bullets: [
            'Top movers and volume spikes',
            'New highs/lows and breakouts',
          ],
        },
      ],
    },
    'sharing': {
      title: 'Sharing Watchlists',
      description: 'Collaborate with team members and friends.',
      readTime: '4 min',
      updated: 'Updated Dec 2024',
      icon: 'Share2',
      sections: [
        {
          title: 'Share Options',
          text: 'Control access and visibility.',
          bullets: [
            'Private, team-only, or public links',
            'Read-only vs. editable permissions',
          ],
        },
        {
          title: 'Embeds & Links',
          text: 'Use lists across tools.',
          bullets: [
            'Embeddable widgets for dashboards',
            'Direct links to filtered views',
          ],
        },
      ],
    },
  },
  'api': {
    'keys': {
      title: 'API Key Management',
      description: 'Generate and manage your API keys securely.',
      readTime: '4 min',
      updated: 'Updated Dec 2024',
      icon: 'KeyRound',
      sections: [
        {
          title: 'Key Lifecycle',
          text: 'Best practices for secure access.',
          bullets: [
            'Create, rotate, and revoke keys regularly',
            'Scope keys to least-privilege access',
          ],
        },
        {
          title: 'Storage',
          text: 'Avoid exposing secrets.',
          bullets: [
            'Use environment variables and secret managers',
            'Never commit secrets to version control',
          ],
        },
      ],
    },
    'limits': {
      title: 'API Rate Limits and Usage',
      description: 'Understand quotas and optimize calls.',
      readTime: '6 min',
      updated: 'Updated Dec 2024',
      icon: 'Gauge',
      sections: [
        {
          title: 'Quotas',
          text: 'Plan capacity and backoffs.',
          bullets: [
            'Per-minute and per-day quotas by plan',
            'HTTP 429 handling and retry-after headers',
          ],
        },
        {
          title: 'Efficiency',
          text: 'Make every request count.',
          bullets: [
            'Batch endpoints and pagination',
            'Conditional requests and caching',
          ],
        },
      ],
    },
    'examples': {
      title: 'Integration Examples',
      description: 'Code samples for common use cases.',
      readTime: '15 min',
      updated: 'Updated Dec 2024',
      icon: 'Code',
      sections: [
        {
          title: 'Fetching Stock Quotes',
          text: 'Language-agnostic patterns for reliability.',
          bullets: [
            'Authentication and retries',
            'Timeouts and circuit breakers',
          ],
        },
        {
          title: 'Webhooks',
          text: 'Receive alerts in your systems.',
          bullets: [
            'Signature verification',
            'Idempotency and retries',
          ],
        },
      ],
    },
    'webhooks': {
      title: 'Webhook Setup',
      description: 'Receive real-time data updates in your applications.',
      readTime: '8 min',
      updated: 'Updated Dec 2024',
      icon: 'Webhook',
      sections: [
        {
          title: 'Endpoint Requirements',
          text: 'Hardened and reliable delivery.',
          bullets: [
            'HTTPS only with TLS 1.2+',
            'HMAC signatures and timestamps',
          ],
        },
        {
          title: 'Reliability',
          text: 'Process each event exactly once.',
          bullets: [
            'Idempotency keys and deduping',
            'Exponential backoff on 5xx/429',
          ],
        },
      ],
    },
  },
};

