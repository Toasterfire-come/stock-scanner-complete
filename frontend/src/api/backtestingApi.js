/**
 * Backtesting API Client
 * Phase 4 - AI Backtesting with Chat Refinement
 */
import { api } from './secureClient';

/**
 * Send a chat message for strategy refinement
 * @param {string} message - User's message
 * @param {Array} conversationHistory - Previous messages
 * @param {string} category - Trading category
 * @returns {Promise<{success: boolean, response?: string, error?: string}>}
 */
export const chatRefineStrategy = async (message, conversationHistory = [], category = 'day_trading') => {
  try {
    const response = await api.post('/backtesting/chat/', {
      message,
      conversation_history: conversationHistory,
      category
    });
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Chat request failed'
    };
  }
};

/**
 * Generate strategy code from description
 * @param {string} strategyDescription - Natural language strategy description
 * @param {string} category - Trading category
 * @returns {Promise<{success: boolean, generated_code?: string, error?: string}>}
 */
export const generateStrategyCode = async (strategyDescription, category = 'day_trading') => {
  try {
    const response = await api.post('/backtesting/generate-code/', {
      strategy_description: strategyDescription,
      category
    });
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Code generation failed'
    };
  }
};

/**
 * Summarize strategy from conversation history
 * @param {Array} conversationHistory - Full conversation history
 * @returns {Promise<{success: boolean, summary?: string, error?: string}>}
 */
export const summarizeStrategy = async (conversationHistory) => {
  try {
    const response = await api.post('/backtesting/summarize/', {
      conversation_history: conversationHistory
    });
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Summarization failed'
    };
  }
};

/**
 * Create a new backtest
 * @param {Object} params - Backtest parameters
 * @returns {Promise<{success: boolean, backtest_id?: number, error?: string}>}
 */
export const createBacktest = async ({
  name,
  strategyText,
  category,
  symbols,
  startDate,
  endDate,
  initialCapital = 10000
}) => {
  try {
    const response = await api.post('/backtesting/create/', {
      name,
      strategy_text: strategyText,
      category,
      symbols: Array.isArray(symbols) ? symbols : [symbols],
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital
    });
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Failed to create backtest'
    };
  }
};

/**
 * Run an existing backtest
 * @param {number} backtestId - ID of the backtest to run
 * @returns {Promise<{success: boolean, results?: Object, error?: string}>}
 */
export const runBacktest = async (backtestId) => {
  try {
    const response = await api.post(`/backtesting/${backtestId}/run/`);
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Failed to run backtest'
    };
  }
};

/**
 * Get backtest details and results
 * @param {number} backtestId - ID of the backtest
 * @returns {Promise<{success: boolean, backtest?: Object, error?: string}>}
 */
export const getBacktest = async (backtestId) => {
  try {
    const response = await api.get(`/backtesting/${backtestId}/`);
    return response.data;
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message || 'Failed to get backtest'
    };
  }
};

/**
 * List all backtests
 * @param {string} category - Optional category filter
 * @returns {Promise<{success: boolean, backtests?: Array, error?: string}>}
 */
export const listBacktests = async (category = null) => {
  try {
    const params = category ? { category } : {};
    const response = await api.get('/backtesting/list/', { params });
    return response.data;
  } catch (error) {
    return {
      success: false,
      backtests: [],
      error: error.response?.data?.error || error.message || 'Failed to list backtests'
    };
  }
};

/**
 * Get baseline strategies
 * @returns {Promise<{success: boolean, strategies?: Array, error?: string}>}
 */
export const getBaselineStrategies = async () => {
  try {
    const response = await api.get('/backtesting/baseline-strategies/');
    return response.data;
  } catch (error) {
    return {
      success: false,
      strategies: [],
      error: error.response?.data?.error || error.message || 'Failed to get baseline strategies'
    };
  }
};

export default {
  chatRefineStrategy,
  generateStrategyCode,
  summarizeStrategy,
  createBacktest,
  runBacktest,
  getBacktest,
  listBacktests,
  getBaselineStrategies
};
