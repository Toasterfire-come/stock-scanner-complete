/**
 * Chart API functions for Phase 3 Advanced Charting
 */
import { api } from './client';

/**
 * Get chart data for a stock
 * @param {string} ticker - Stock ticker symbol
 * @param {object} options - Options for chart data
 * @param {string} options.timeframe - Chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo)
 * @param {string} options.chartType - Chart type (candlestick, line, area, heikin_ashi)
 * @param {string} options.start - Start date (YYYY-MM-DD)
 * @param {string} options.end - End date (YYYY-MM-DD)
 */
export async function getChartData(ticker, options = {}) {
  try {
    const params = {
      timeframe: options.timeframe || '1d',
      chart_type: options.chartType || 'candlestick',
    };
    if (options.start) params.start = options.start;
    if (options.end) params.end = options.end;

    const { data } = await api.get(`/chart/${encodeURIComponent(ticker.toUpperCase())}/`, { params });
    return data;
  } catch (error) {
    console.error('Failed to fetch chart data:', error);
    return { success: false, error: error.message || 'Failed to load chart data' };
  }
}

/**
 * Get technical indicators for a stock
 * @param {string} ticker - Stock ticker symbol
 * @param {object} options - Options for indicators
 * @param {string[]} options.indicators - Array of indicator IDs
 * @param {string} options.timeframe - Chart timeframe
 */
export async function getChartIndicators(ticker, options = {}) {
  try {
    const params = {
      timeframe: options.timeframe || '1d',
      indicators: Array.isArray(options.indicators) 
        ? options.indicators.join(',') 
        : 'sma_20,ema_50',
    };

    const { data } = await api.get(`/chart/${encodeURIComponent(ticker.toUpperCase())}/indicators/`, { params });
    return data;
  } catch (error) {
    console.error('Failed to fetch indicators:', error);
    return { success: false, error: error.message || 'Failed to load indicators' };
  }
}

/**
 * Get available chart timeframes and options
 */
export async function getChartTimeframes() {
  try {
    const { data } = await api.get('/chart/timeframes/');
    return data;
  } catch (error) {
    console.error('Failed to fetch timeframes:', error);
    return { success: false, error: error.message || 'Failed to load chart options' };
  }
}

export default {
  getChartData,
  getChartIndicators,
  getChartTimeframes,
};
