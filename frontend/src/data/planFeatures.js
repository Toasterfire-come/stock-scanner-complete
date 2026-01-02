/**
 * Centralized Plan Features Configuration
 * ===========================================
 * This is the single source of truth for all plan features and pricing.
 * Use this file consistently across ALL pages (Home, Pricing, PricingPro, etc.)
 * to avoid inconsistencies in feature claims.
 *
 * Last Updated: December 29, 2025
  * Updated: Pricing from Bronze/Silver/Gold to Basic/Pro plans
 */

export const PLAN_FEATURES = {
  // FREE PLAN - Currently NOT offered (removed per business policy)
  // Kept here for reference only - DO NOT display unless business policy changes
  free: {
    id: 'free',
    name: 'Free',
    price: 0,
    priceMonthly: 0,
    priceAnnual: 0,
    isActive: false, // Set to true to re-enable
    description: 'Perfect for getting started',
    apiCalls: {
      total: 30,
      period: 'month',
      daily: null,
      description: '30 API calls per month'
    },
    screeners: {
      count: 1,
      type: 'basic',
      description: '1 Basic stock screener'
    },
    watchlists: {
      count: 1,
      description: '1 Watchlist'
    },
    portfolios: {
      count: 1,
      description: '1 Portfolio'
    },
    alerts: {
      count: 0,
      description: 'No alerts'
    },
    support: 'Community',
    features: [
      '30 API calls per month',
      'Basic stock data access',
      '1 Basic stock screener',
      '1 Watchlist',
      '1 Portfolio',
      'Community support'
    ]
  },

  // BASIC PLAN - Essential for active traders
  basic: {
    id: 'basic',
    name: 'Basic',
    price: 9.99,
    priceMonthly: 9.99,
    priceAnnual: 101.99, // ~15% discount (9.99 * 12 * 0.85 = 101.9)
    isActive: true,
    popular: true,
    description: 'Essential features for active traders',
    apiCalls: {
      total: 2500,
      period: 'month',
      daily: 83, // Average: 2500 / 30 ≈ 83
      description: '2,500 API calls per month (83 daily average)'
    },
    screeners: {
      count: 5,
      type: 'standard',
      medianTimeMinutes: 9,
      runsPerMonth: 50,
      description: '5 saved screeners, 50 runs per month'
    },
    watchlists: {
      count: 3,
      stocksPerList: 50,
      description: '3 watchlists with up to 50 stocks each'
    },
    portfolios: {
      count: 2,
      holdingsPerPortfolio: 25,
      description: '2 portfolios with up to 25 holdings each'
    },
    alerts: {
      count: 25,
      period: 'month',
      description: '25 active alerts'
    },
    charting: {
      provider: 'Stooq',
      types: ['Standard', 'Volume Profile'],
      exports: 20,
      description: 'Stooq charting with standard and volume profile'
    },
    dataDelay: '15 minutes',
    support: 'Email',
    features: [
      '2,500 API calls per month (83 daily average)',
      '5 saved screeners, 50 runs per month',
      '25 active alerts with SMS notifications',
      '3 watchlists with up to 50 stocks each',
      '2 portfolios with up to 25 holdings each',
      'Stooq charting (standard + volume profile)',
      'Core indicators & automated technical summaries',
      'Financial statements & fundamentals',
      'News + sentiment analysis',
      'Economic calendar (earnings, Fed decisions)',
      'Manual paper trading',
      'Mobile chart viewing',
      'Education & help resources',
      'Security features (MFA, encryption)',
      'Email support'
    ]
  },

  // PRO PLAN - Professional tools for serious traders
  pro: {
    id: 'pro',
    name: 'Pro',
    price: 24.99,
    priceMonthly: 24.99,
    priceAnnual: 254.99, // ~15% discount (24.99 * 12 * 0.85 = 254.9)
    isActive: true,
    popular: false,
    description: 'Professional tools for serious traders',
    apiCalls: {
      total: 10000,
      period: 'month',
      daily: 333, // Average: 10000 / 30 ≈ 333
      description: '10,000 API calls per month (333 daily average)'
    },
    screeners: {
      count: 25,
      type: 'advanced',
      medianTimeMinutes: 9,
      runsPerMonth: 500,
      description: '25 saved screeners, 500 runs per month'
    },
    watchlists: {
      count: 10,
      stocksPerList: 'unlimited',
      description: '10 watchlists with unlimited stocks'
    },
    portfolios: {
      count: 10,
      holdingsPerPortfolio: 'unlimited',
      description: '10 portfolios with unlimited holdings'
    },
    alerts: {
      count: 150,
      period: 'month',
      description: '150 active alerts'
    },
    charting: {
      provider: 'TradingView',
      types: ['Standard', 'Volume Profile', 'Heikin Ashi', 'Renko', 'Point & Figure'],
      exports: 200,
      description: 'TradingView Premium with exotic chart types'
    },
    backtests: {
      count: 50,
      period: 'month',
      description: '50 AI backtests per month'
    },
    dataDelay: 'Real-time',
    support: 'Priority Email',
    features: [
      '10,000 API calls per month (333 daily average)',
      '25 saved screeners, 500 runs per month',
      '150 active alerts with SMS and webhook notifications',
      '10 watchlists with unlimited stocks',
      '10 portfolios with unlimited holdings',
      'TradingView Premium charting',
      'Advanced indicators (VWAP, Ichimoku, etc.)',
      'Fair value & DCF analysis tools',
      '50 AI-powered backtests per month',
      'Portfolio tracking & analytics',
      'Multi-condition webhook alerts',
      'Insider trading activity feed',
      'Options analytics (Greeks, IV surfaces)',
      'Social features (follow traders, clone strategies)',
      'Real-time market data',
      'Priority support & onboarding',
      'Early access to new features'
    ]
  },

  // PAY-PER-USE PLAN - Flexible usage-based pricing
  payPerUse: {
    id: 'pay-per-use',
    name: 'Pay-Per-Use',
    price: 24.99,
    priceMonthly: 24.99,
    priceAnnual: 254.99, // ~15% discount (24.99 * 12 * 0.85 = 254.9)
    isActive: true,
    popular: false,
    description: 'Flexible pricing for seasonal traders and developers',
    baseAllocation: {
      apiCalls: 10000,
      screeners: 25,
      screenerRuns: 500,
      alerts: 150,
      watchlists: 10,
      portfolios: 10,
      chartExports: 200,
      aiBacktests: 50
    },
    overagePricing: {
      apiCall: 0.001, // $0.001 per call = $1 per 1,000 calls
      screenerRun: 0.10,
      aiBacktest: 0.25,
      chartExport: 0.02,
      watchlist: 1.00, // per additional list
      portfolio: 2.00  // per additional portfolio
    },
    hardCaps: {
      apiCalls: 100000, // max 100K API calls per month
      totalBill: 124.99  // max $124.99/month (base $24.99 + $100 overages)
    },
    notifications: {
      thresholds: [50, 75, 90, 100], // notify at these % of limits
      autoPauseAtCap: true
    },
    apiCalls: {
      total: 10000,
      period: 'month',
      daily: 333,
      description: '10,000 API calls per month base (333 daily average), then $1 per 1,000 additional calls'
    },
    screeners: {
      count: 25,
      type: 'advanced',
      medianTimeMinutes: 9,
      runsPerMonth: 500,
      description: '25 saved screeners, 500 runs per month base, then $0.10 per additional run'
    },
    watchlists: {
      count: 10,
      stocksPerList: 'unlimited',
      description: '10 watchlists base, then $1.00 per additional watchlist'
    },
    portfolios: {
      count: 10,
      holdingsPerPortfolio: 'unlimited',
      description: '10 portfolios base, then $2.00 per additional portfolio'
    },
    alerts: {
      count: 150,
      period: 'month',
      description: '150 active alerts (included in base)'
    },
    charting: {
      provider: 'TradingView',
      types: ['Standard', 'Volume Profile', 'Heikin Ashi', 'Renko', 'Point & Figure'],
      exports: 200,
      description: 'TradingView Premium, 200 exports base, then $0.02 per additional export'
    },
    backtests: {
      count: 50,
      period: 'month',
      description: '50 AI backtests base, then $0.25 per additional backtest'
    },
    dataDelay: 'Real-time',
    support: 'Priority Email',
    features: [
      'Everything in Pro, plus:',
      'Pay only for what you use beyond base allocation',
      'Hard cap at $124.99/month (no surprise bills)',
      'Notifications at 50%, 75%, 90%, 100% usage',
      'Auto-pause at usage cap (configurable)',
      'Perfect for seasonal trading patterns',
      'Ideal for algorithm developers',
      'Detailed usage analytics and forecasting',
      'Monthly usage reports with cost breakdown',
      'Flexible - scale up or down anytime'
    ]
  }
};

/**
 * Trial Configuration
 * -------------------
 * Defines trial terms for all paid plans
 */
export const TRIAL_TERMS = {
  enabled: true,
  durationDays: 14,
  requiresCreditCard: false,
  autoRenew: true,
  cancellationPolicy: 'Cancel anytime before trial ends',
  description: '14-day free trial, no credit card required',
  fullDescription: 'Start your 14-day free trial today. No credit card required. Cancel anytime before the trial ends to avoid charges. After the trial, your selected plan will automatically begin at the standard monthly rate.',
  disclaimers: [
    'Free trial available for new users only',
    'One trial per user',
    'Credit card required for automatic renewal after trial',
    'Cancel before trial ends to avoid charges'
  ]
};

/**
 * Helper function to get active plans only
 */
export const getActivePlans = () => {
  return Object.values(PLAN_FEATURES).filter(plan => plan.isActive);
};

/**
 * Helper function to get plan by ID
 */
export const getPlanById = (planId) => {
  return PLAN_FEATURES[planId] || null;
};

/**
 * Helper function to format API calls description
 */
export const formatApiCallsDescription = (plan) => {
  if (!plan.apiCalls) return '';
  const { total, period, daily } = plan.apiCalls;
  if (daily) {
    return `${total.toLocaleString()} API calls per ${period} (${daily} daily average)`;
  }
  return `${total.toLocaleString()} API calls per ${period}`;
};

/**
 * Helper function to calculate annual savings
 */
export const calculateAnnualSavings = (plan) => {
  if (!plan.priceMonthly || !plan.priceAnnual) return 0;
  const annualIfMonthly = plan.priceMonthly * 12;
  const savings = annualIfMonthly - plan.priceAnnual;
  return Math.round(savings * 100) / 100;
};

/**
 * Helper function to calculate discount percentage
 */
export const calculateDiscountPercent = (plan) => {
  if (!plan.priceMonthly || !plan.priceAnnual) return 0;
  const annualIfMonthly = plan.priceMonthly * 12;
  const discount = ((annualIfMonthly - plan.priceAnnual) / annualIfMonthly) * 100;
  return Math.round(discount);
};

// Export default for convenience
export default PLAN_FEATURES;
