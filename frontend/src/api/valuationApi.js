/**
 * Valuation API functions for Phase 2 Valuation Engine
 */
import { api } from './client';
import logger from '../lib/logger';

/**
 * Get comprehensive stock valuation analysis
 * @param {string} ticker - Stock ticker symbol
 */
export async function getStockValuation(ticker) {
  try {
    const { data } = await api.get(`/valuation/${encodeURIComponent(ticker.toUpperCase())}/`);
    return data;
  } catch (error) {
    logger.error('Failed to fetch valuation:', error);
    return { success: false, error: error.message || 'Failed to load valuation data' };
  }
}

/**
 * Get quick valuation summary (lighter weight)
 * @param {string} ticker - Stock ticker symbol
 */
export async function getQuickValuation(ticker) {
  try {
    const { data } = await api.get(`/valuation/${encodeURIComponent(ticker.toUpperCase())}/quick/`);
    return data;
  } catch (error) {
    logger.error('Failed to fetch quick valuation:', error);
    return { success: false, error: error.message || 'Failed to load valuation' };
  }
}

/**
 * Get undervalued stocks screener results
 * @param {object} options - Screener options
 * @param {number} options.minScore - Minimum valuation score (default: 60)
 * @param {number} options.minMarketCap - Minimum market cap in billions
 * @param {string} options.sector - Filter by sector
 * @param {number} options.limit - Number of results
 */
export async function getUndervaluedStocks(options = {}) {
  try {
    const params = {};
    if (options.minScore) params.min_score = options.minScore;
    if (options.minMarketCap) params.min_market_cap = options.minMarketCap;
    if (options.sector) params.sector = options.sector;
    if (options.limit) params.limit = options.limit;

    const { data } = await api.get('/screener/undervalued/', { params });
    return data;
  } catch (error) {
    logger.error('Failed to fetch undervalued stocks:', error);
    return { success: false, error: error.message || 'Failed to load screener results' };
  }
}

/**
 * Sync stock fundamentals from yfinance to database
 * @param {string} ticker - Stock ticker symbol
 */
export async function syncStockFundamentals(ticker) {
  try {
    const { data } = await api.post(`/fundamentals/${encodeURIComponent(ticker.toUpperCase())}/sync/`);
    return data;
  } catch (error) {
    logger.error('Failed to sync fundamentals:', error);
    return { success: false, error: error.message || 'Failed to sync fundamentals' };
  }
}

/**
 * Get sector-level valuation analysis
 */
export async function getSectorAnalysis() {
  try {
    const { data } = await api.get('/valuation/sectors/');
    return data;
  } catch (error) {
    logger.error('Failed to fetch sector analysis:', error);
    return { success: false, error: error.message || 'Failed to load sector analysis' };
  }
}

/**
 * Get top value stocks
 * @param {object} options - Filter options
 * @param {string} options.sector - Filter by sector
 * @param {number} options.minMarketCap - Minimum market cap in billions
 * @param {number} options.limit - Number of results
 */
export async function getTopValueStocks(options = {}) {
  try {
    const params = {};
    if (options.sector) params.sector = options.sector;
    if (options.minMarketCap) params.min_market_cap = options.minMarketCap;
    if (options.limit) params.limit = options.limit;

    const { data } = await api.get('/valuation/top-value/', { params });
    return data;
  } catch (error) {
    logger.error('Failed to fetch top value stocks:', error);
    return { success: false, error: error.message || 'Failed to load top value stocks' };
  }
}

/**
 * Compare valuations of multiple stocks
 * @param {string[]} tickers - Array of ticker symbols
 */
export async function compareValuations(tickers) {
  try {
    const { data } = await api.get('/valuation/compare/', {
      params: { tickers: tickers.join(',') }
    });
    return data;
  } catch (error) {
    logger.error('Failed to compare valuations:', error);
    return { success: false, error: error.message || 'Failed to compare stocks' };
  }
}

/**
 * Get comprehensive fundamentals for a stock
 * @param {string} ticker - Stock ticker symbol
 */
export async function getStockFundamentals(ticker) {
  try {
    const { data } = await api.get(`/fundamentals/${encodeURIComponent(ticker.toUpperCase())}/`);
    return data;
  } catch (error) {
    logger.error('Failed to fetch fundamentals:', error);
    return { success: false, error: error.message || 'Failed to load fundamentals' };
  }
}

export default {
  getStockValuation,
  getQuickValuation,
  getUndervaluedStocks,
  syncStockFundamentals,
  getSectorAnalysis,
  getTopValueStocks,
  compareValuations,
  getStockFundamentals,
};
