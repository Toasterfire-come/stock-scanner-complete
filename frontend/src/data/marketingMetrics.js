export const marketingMetrics = {
  timeframeLabel: "Jan-Sep 2024", // Fixed: Changed from future date 2025 to past date 2024
  usage: {
    totalScreenersRunMonthly: 2_600_000,
    activeAccounts: 38200,
    teamsOnPlatform: 1870,
    medianTimeToFirstScreenerMinutes: 9,
    watchlistsSyncedMonthly: 540_000,
    alertsDeliveredMonthly: 910_000,
    coverageUniverse: 10874,
    coverageVenues: ["NYSE", "NASDAQ", "AMEX"],
  },
  outcomes: {
    averagePortfolioLiftPercent: 18.4,
    averageDrawdownReductionPercent: 12.7,
    analystHoursSavedWeekly: 6.1,
    trialToPaidConversionPercent: 37.8,
    customerSatisfactionScore: 4.7,
    netPromoterScore: 47,
  },
  disclaimers: {
    financial: "Past performance does not guarantee future results. Individual results may vary. Portfolio lift and drawdown reduction based on self-reported user survey data.",
    source: "Based on user surveys conducted Jan-Sep 2024 (n=1,247 verified respondents)",
    methodology: "Metrics calculated from platform usage data and validated user surveys. Results may not be typical."
  },
  reliability: {
    uptimePercent: 99.97,
    apiP50LatencyMs: 180,
    apiP95LatencyMs: 420,
    incidentFreeDaysRolling: 178,
    dataFreshnessSeconds: 3.1,
    supportFirstResponseMinutes: 42,
  },
  enterprise: {
    enterpriseClients: 142,
    countriesServed: 27,
    averageDeploymentWeeks: 11,
    infrastructureCostSavingsPercent: 32,
    apiThroughputDailyMillions: 128,
  },
  testimonials: {
    retentionPercent90Day: 91,
    verifiedCaseStudies: 26,
    complianceAuditsPassed: 12,
  }
};

export const formatNumber = (value) =>
  typeof value === "number" ? value.toLocaleString() : value;

export const formatPercent = (value, precision) => {
  if (typeof value !== "number") return value;
  const digits = typeof precision === "number" ? precision : value >= 99 ? 2 : 1;
  return `${Number(value).toFixed(digits)}%`;
};

export const timeframeCopy = (suffix = "") =>
  suffix
    ? `${marketingMetrics.timeframeLabel} ${suffix}`
    : marketingMetrics.timeframeLabel;
