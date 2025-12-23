/**
 * Centralized Plan Features Configuration
 * ===========================================
 * This is the single source of truth for all plan features and pricing.
 * Use this file consistently across ALL pages (Home, Pricing, PricingPro, etc.)
 * to avoid inconsistencies in feature claims.
 *
 * Last Updated: December 22, 2024
 * QA Issue: #9 - Feature Claims Inconsistency Fix
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

  // BRONZE PLAN - Entry level paid plan
  bronze: {
    id: 'bronze',
    name: 'Bronze',
    price: 24.99,
    priceMonthly: 24.99,
    priceAnnual: 254.99, // ~15% discount (24.99 * 12 * 0.85 = 254.9)
    isActive: true,
    popular: true,
    description: 'Enhanced features for active traders',
    apiCalls: {
      total: 1500,
      period: 'month',
      daily: 50, // Average: 1500 / 30 = 50
      description: '1,500 API calls per month (50 daily average)'
    },
    screeners: {
      count: 10,
      type: 'standard',
      medianTimeMinutes: 9,
      description: '10 Screeners with 9 min median time'
    },
    watchlists: {
      count: 2,
      description: '2 Watchlists'
    },
    portfolios: {
      count: 0,
      description: 'No portfolios'
    },
    alerts: {
      count: 50,
      period: 'month',
      description: '50 Alerts per month'
    },
    support: 'Email',
    features: [
      '1,500 API calls per month (50 daily average)',
      '10 Screeners with 9 min median time',
      '50 Alerts per month',
      '2 Watchlists',
      'No portfolios',
      'Professional stock data access',
      'Real-time market information',
      'High Quality News and Sentiment Analysis',
      'Email support'
    ]
  },

  // SILVER PLAN - Mid-tier plan
  silver: {
    id: 'silver',
    name: 'Silver',
    price: 49.99,
    priceMonthly: 49.99,
    priceAnnual: 509.99, // ~15% discount
    isActive: true,
    popular: false,
    description: 'Advanced features for serious traders',
    apiCalls: {
      total: 5000,
      period: 'month',
      daily: 166, // Average: 5000 / 30 ≈ 166
      description: '5,000 API calls per month (166 daily average)'
    },
    screeners: {
      count: 25,
      type: 'advanced',
      medianTimeMinutes: 9,
      description: '25 Screeners with 9 min median time'
    },
    watchlists: {
      count: 5,
      description: '5 Watchlists'
    },
    portfolios: {
      count: 3,
      description: '3 Portfolios'
    },
    alerts: {
      count: 150,
      period: 'month',
      description: '150 Alerts per month'
    },
    support: 'Priority Email',
    features: [
      '5,000 API calls per month (166 daily average)',
      '25 Screeners with 9 min median time',
      '150 Alerts per month',
      '5 Watchlists',
      '3 Portfolios',
      'Professional stock data access',
      'Real-time market information',
      'High Quality News and Sentiment Analysis',
      'AI-powered backtesting',
      'Priority email support'
    ]
  },

  // GOLD PLAN - Premium plan
  gold: {
    id: 'gold',
    name: 'Gold',
    price: 99.99,
    priceMonthly: 99.99,
    priceAnnual: 1019.99, // ~15% discount
    isActive: true,
    popular: false,
    description: 'Professional-grade features',
    apiCalls: {
      total: 15000,
      period: 'month',
      daily: 500, // Average: 15000 / 30 = 500
      description: '15,000 API calls per month (500 daily average)'
    },
    screeners: {
      count: 'unlimited',
      type: 'professional',
      medianTimeMinutes: 9,
      description: 'Unlimited Screeners with 9 min median time'
    },
    watchlists: {
      count: 'unlimited',
      description: 'Unlimited Watchlists'
    },
    portfolios: {
      count: 10,
      description: '10 Portfolios'
    },
    alerts: {
      count: 500,
      period: 'month',
      description: '500 Alerts per month'
    },
    support: 'Priority Support',
    features: [
      '15,000 API calls per month (500 daily average)',
      'Unlimited Screeners with 9 min median time',
      '500 Alerts per month',
      'Unlimited Watchlists',
      '10 Portfolios',
      'Professional stock data access',
      'Real-time market information',
      'High Quality News and Sentiment Analysis',
      'AI-powered backtesting',
      'Advanced portfolio analytics',
      'Priority support'
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
