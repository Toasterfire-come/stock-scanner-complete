// Mock data for the stock scanner application
export const mockData = {
  // Market stats for the homepage
  marketStats: {
    total_stocks: 10847,
    gainers: 3421,
    losers: 2156,
    unchanged: 5270,
    volume: 8500000000,
    market_cap: 45000000000000
  },

  // Sample stocks data
  stocks: [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      price: 185.42,
      change: 2.45,
      changePercent: 1.34,
      volume: 45678901,
      marketCap: 2890000000000,
      sector: "Technology",
      industry: "Consumer Electronics",
      peRatio: 29.8,
      dividend: 0.94,
      fiftyTwoWeekHigh: 199.62,
      fiftyTwoWeekLow: 164.08,
      beta: 1.25
    },
    {
      symbol: "GOOGL",
      name: "Alphabet Inc.",
      price: 142.65,
      change: -1.82,
      changePercent: -1.26,
      volume: 23456789,
      marketCap: 1780000000000,
      sector: "Technology",
      industry: "Internet Services",
      peRatio: 24.3,
      dividend: 0.00,
      fiftyTwoWeekHigh: 153.78,
      fiftyTwoWeekLow: 121.46,
      beta: 1.12
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      price: 415.33,
      change: 5.67,
      changePercent: 1.38,
      volume: 34567890,
      marketCap: 3080000000000,
      sector: "Technology",
      industry: "Software",
      peRatio: 31.2,
      dividend: 2.72,
      fiftyTwoWeekHigh: 468.35,
      fiftyTwoWeekLow: 362.90,
      beta: 0.91
    },
    {
      symbol: "TSLA",
      name: "Tesla, Inc.",
      price: 248.74,
      change: 12.45,
      changePercent: 5.27,
      volume: 78901234,
      marketCap: 790000000000,
      sector: "Consumer Discretionary",
      industry: "Auto Manufacturers",
      peRatio: 62.4,
      dividend: 0.00,
      fiftyTwoWeekHigh: 299.29,
      fiftyTwoWeekLow: 138.80,
      beta: 2.34
    },
    {
      symbol: "AMZN",
      name: "Amazon.com, Inc.",
      price: 178.35,
      change: -2.15,
      changePercent: -1.19,
      volume: 56789012,
      marketCap: 1850000000000,
      sector: "Consumer Discretionary",
      industry: "Internet Retail",
      peRatio: 45.7,
      dividend: 0.00,
      fiftyTwoWeekHigh: 201.20,
      fiftyTwoWeekLow: 144.05,
      beta: 1.15
    }
  ],

  // Market sectors data
  sectors: [
    { name: "Technology", change: 1.45, stocks: 847, topGainer: "NVDA", topLoser: "INTC" },
    { name: "Healthcare", change: 0.87, stocks: 623, topGainer: "JNJ", topLoser: "PFE" },
    { name: "Financials", change: -0.32, stocks: 456, topGainer: "JPM", topLoser: "BAC" },
    { name: "Consumer Discretionary", change: 2.14, stocks: 389, topGainer: "TSLA", topLoser: "HD" },
    { name: "Communication Services", change: -0.89, stocks: 234, topGainer: "META", topLoser: "DIS" },
    { name: "Industrials", change: 0.56, stocks: 345, topGainer: "GE", topLoser: "CAT" },
    { name: "Consumer Staples", change: -0.12, stocks: 167, topGainer: "WMT", topLoser: "KO" },
    { name: "Energy", change: 3.21, stocks: 123, topGainer: "XOM", topLoser: "CVX" },
    { name: "Utilities", change: -0.45, stocks: 89, topGainer: "NEE", topLoser: "DUK" },
    { name: "Real Estate", change: 1.23, stocks: 67, topGainer: "AMT", topLoser: "PLD" },
    { name: "Materials", change: 0.78, stocks: 98, topGainer: "LIN", topLoser: "DOW" }
  ],

  // Watchlists
  watchlists: [
    {
      id: 1,
      name: "Tech Giants",
      description: "Large cap technology companies",
      stocks: ["AAPL", "GOOGL", "MSFT", "AMZN", "META"],
      created: "2025-01-10",
      isPublic: false
    },
    {
      id: 2,
      name: "Growth Stocks",
      description: "High growth potential stocks",
      stocks: ["TSLA", "NVDA", "AMD", "ROKU", "SQ"],
      created: "2025-01-08",
      isPublic: true
    },
    {
      id: 3,
      name: "Dividend Aristocrats",
      description: "Stocks with consistent dividend payments",
      stocks: ["JNJ", "PG", "KO", "MCD", "WMT"],
      created: "2025-01-05",
      isPublic: false
    }
  ],

  // Alerts
  alerts: [
    {
      id: 1,
      symbol: "AAPL",
      type: "price",
      condition: "above",
      value: 180,
      currentPrice: 185.42,
      triggered: true,
      created: "2025-01-10",
      message: "AAPL price crossed above $180"
    },
    {
      id: 2,
      symbol: "TSLA",
      type: "volume",
      condition: "above",
      value: 50000000,
      currentVolume: 78901234,
      triggered: true,
      created: "2025-01-10",
      message: "TSLA volume exceeded 50M shares"
    },
    {
      id: 3,
      symbol: "GOOGL",
      type: "price",
      condition: "below",
      value: 140,
      currentPrice: 142.65,
      triggered: false,
      created: "2025-01-09",
      message: "GOOGL price alert at $140"
    }
  ],

  // Portfolio data
  portfolio: {
    totalValue: 125450.75,
    dayChange: 2145.30,
    dayChangePercent: 1.74,
    totalGainLoss: 15420.50,
    totalGainLossPercent: 14.08,
    holdings: [
      {
        symbol: "AAPL",
        name: "Apple Inc.",
        shares: 50,
        avgCost: 172.50,
        currentPrice: 185.42,
        totalValue: 9271.00,
        gainLoss: 646.00,
        gainLossPercent: 7.48
      },
      {
        symbol: "MSFT",
        name: "Microsoft Corporation",
        shares: 25,
        avgCost: 395.20,
        currentPrice: 415.33,
        totalValue: 10383.25,
        gainLoss: 503.25,
        gainLossPercent: 5.08
      },
      {
        symbol: "GOOGL",
        name: "Alphabet Inc.",
        shares: 30,
        avgCost: 138.75,
        currentPrice: 142.65,
        totalValue: 4279.50,
        gainLoss: 117.00,
        gainLossPercent: 2.81
      }
    ]
  },

  // News data
  news: [
    {
      id: 1,
      title: "Tesla Reports Strong Q4 Earnings, Stock Surges",
      summary: "Tesla exceeded analyst expectations with record deliveries and improved margins in the fourth quarter.",
      source: "MarketWatch",
      publishedAt: "2025-01-10T14:30:00Z",
      url: "#",
      sentiment: "positive",
      relatedSymbols: ["TSLA"]
    },
    {
      id: 2,
      title: "Federal Reserve Signals Potential Rate Cut",
      summary: "Fed officials hint at possible interest rate reduction in upcoming meeting, boosting market sentiment.",
      source: "Reuters",
      publishedAt: "2025-01-10T12:15:00Z",
      url: "#",
      sentiment: "positive",
      relatedSymbols: ["SPY", "QQQ"]
    },
    {
      id: 3,
      title: "Apple Faces Regulatory Challenges in Europe",
      summary: "European Union proposes new regulations that could impact Apple's App Store revenue model.",
      source: "Financial Times",
      publishedAt: "2025-01-10T09:45:00Z",
      url: "#",
      sentiment: "negative",
      relatedSymbols: ["AAPL"]
    },
    {
      id: 4,
      title: "Microsoft Azure Gains Market Share",
      summary: "Cloud computing division shows strong growth, competing effectively with Amazon AWS.",
      source: "TechCrunch",
      publishedAt: "2025-01-09T16:20:00Z",
      url: "#",
      sentiment: "positive",
      relatedSymbols: ["MSFT", "AMZN"]
    }
  ],

  // Screener criteria options
  screenerCriteria: {
    fundamental: [
      { key: "marketCap", label: "Market Cap", type: "range", unit: "billion" },
      { key: "peRatio", label: "P/E Ratio", type: "range", unit: "" },
      { key: "priceToBook", label: "Price to Book", type: "range", unit: "" },
      { key: "dividend", label: "Dividend Yield", type: "range", unit: "%" },
      { key: "roe", label: "Return on Equity", type: "range", unit: "%" },
      { key: "debtToEquity", label: "Debt to Equity", type: "range", unit: "" },
      { key: "revenueGrowth", label: "Revenue Growth", type: "range", unit: "%" },
      { key: "earningsGrowth", label: "Earnings Growth", type: "range", unit: "%" }
    ],
    technical: [
      { key: "price", label: "Price", type: "range", unit: "$" },
      { key: "volume", label: "Volume", type: "range", unit: "M" },
      { key: "rsi", label: "RSI (14)", type: "range", unit: "" },
      { key: "sma20", label: "20-day SMA", type: "comparison", unit: "$" },
      { key: "sma50", label: "50-day SMA", type: "comparison", unit: "$" },
      { key: "sma200", label: "200-day SMA", type: "comparison", unit: "$" },
      { key: "changePercent", label: "% Change", type: "range", unit: "%" },
      { key: "beta", label: "Beta", type: "range", unit: "" }
    ],
    descriptive: [
      { key: "sector", label: "Sector", type: "select", options: ["Technology", "Healthcare", "Financials", "Consumer Discretionary", "Communication Services", "Industrials", "Consumer Staples", "Energy", "Utilities", "Real Estate", "Materials"] },
      { key: "industry", label: "Industry", type: "text" },
      { key: "country", label: "Country", type: "select", options: ["United States", "Canada", "United Kingdom", "Germany", "Japan", "China"] },
      { key: "exchange", label: "Exchange", type: "select", options: ["NASDAQ", "NYSE", "AMEX"] }
    ]
  },

  // Dashboard metrics
  dashboardMetrics: {
    portfolioValue: 125450.75,
    dayChange: 2145.30,
    activeAlerts: 12,
    watchlistCount: 3,
    topGainer: { symbol: "TSLA", change: 5.27 },
    topLoser: { symbol: "GOOGL", change: -1.26 },
    marketStatus: "Open",
    lastUpdated: new Date().toISOString()
  }
};