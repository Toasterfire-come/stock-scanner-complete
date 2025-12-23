/**
 * Application Logger Utility
 * ===========================
 * Replaces console.log/error/warn statements throughout the application
 *
 * QA Fix: Issue #6 - Remove 117 console statements from production
 *
 * Usage:
 *   import { logger } from '@/lib/logger';
 *
 *   logger.log('Debug info');           // Only in development
 *   logger.error('Error occurred', err); // Sent to Sentry in production
 *   logger.warn('Warning message');      // Only in development
 *   logger.info('Info message');         // Only in development
 *
 * Benefits:
 *   - No console clutter in production
 *   - Automatic error tracking via Sentry
 *   - Performance improvement (no logging overhead)
 *   - Prevents sensitive data leakage
 */

const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

// Sentry integration (if available)
let Sentry;
try {
  // Dynamically import Sentry if it exists
  Sentry = require('@sentry/react');
} catch (e) {
  // Sentry not installed, will use fallback
  Sentry = null;
}

/**
 * Logger object with methods for different log levels
 */
export const logger = {
  /**
   * Debug logging - only in development
   * @param {...any} args - Arguments to log
   */
  log: (...args) => {
    if (isDevelopment) {
      console.log('[LOG]', ...args);
    }
  },

  /**
   * Error logging - logs in development, sends to Sentry in production
   * @param {string} message - Error message
   * @param {Error|any} error - Error object or additional context
   */
  error: (message, error) => {
    if (isDevelopment) {
      console.error('[ERROR]', message, error);
    }

    if (isProduction && Sentry) {
      // Send to Sentry in production
      if (error instanceof Error) {
        Sentry.captureException(error, {
          tags: { source: 'logger' },
          extra: { message }
        });
      } else {
        Sentry.captureMessage(message, {
          level: 'error',
          extra: { error }
        });
      }
    }
  },

  /**
   * Warning logging - only in development
   * @param {...any} args - Arguments to log
   */
  warn: (...args) => {
    if (isDevelopment) {
      console.warn('[WARN]', ...args);
    }
  },

  /**
   * Info logging - only in development
   * @param {...any} args - Arguments to log
   */
  info: (...args) => {
    if (isDevelopment) {
      console.info('[INFO]', ...args);
    }
  },

  /**
   * Debug logging with trace - only in development
   * @param {...any} args - Arguments to log
   */
  debug: (...args) => {
    if (isDevelopment) {
      console.debug('[DEBUG]', ...args);
      console.trace();
    }
  },

  /**
   * Group logging - only in development
   * @param {string} label - Group label
   * @param {Function} callback - Function to execute within group
   */
  group: (label, callback) => {
    if (isDevelopment) {
      console.group(label);
      callback();
      console.groupEnd();
    } else {
      callback();
    }
  },

  /**
   * Table logging - only in development
   * @param {any} data - Data to display as table
   */
  table: (data) => {
    if (isDevelopment) {
      console.table(data);
    }
  },

  /**
   * Time measurement - only in development
   * @param {string} label - Timer label
   */
  time: (label) => {
    if (isDevelopment) {
      console.time(label);
    }
  },

  /**
   * End time measurement - only in development
   * @param {string} label - Timer label
   */
  timeEnd: (label) => {
    if (isDevelopment) {
      console.timeEnd(label);
    }
  }
};

/**
 * API request logger - tracks API calls in development
 * @param {string} method - HTTP method
 * @param {string} url - Request URL
 * @param {any} data - Request data
 */
export const logApiRequest = (method, url, data) => {
  if (isDevelopment) {
    logger.group(`API ${method} ${url}`, () => {
      logger.log('Request:', data);
      logger.log('Timestamp:', new Date().toISOString());
    });
  }
};

/**
 * API response logger - tracks API responses in development
 * @param {string} method - HTTP method
 * @param {string} url - Request URL
 * @param {any} response - Response data
 * @param {number} duration - Request duration in ms
 */
export const logApiResponse = (method, url, response, duration) => {
  if (isDevelopment) {
    logger.group(`API ${method} ${url} - ${duration}ms`, () => {
      logger.log('Response:', response);
      logger.log('Duration:', `${duration}ms`);
    });
  }
};

/**
 * Component render logger - for debugging re-renders
 * @param {string} componentName - Name of component
 * @param {any} props - Component props
 */
export const logComponentRender = (componentName, props) => {
  if (isDevelopment && process.env.REACT_APP_LOG_RENDERS === 'true') {
    logger.log(`🔄 ${componentName} rendered`, props);
  }
};

/**
 * Redux action logger (if using Redux)
 * @param {string} action - Action type
 * @param {any} payload - Action payload
 */
export const logAction = (action, payload) => {
  if (isDevelopment) {
    logger.group(`Redux Action: ${action}`, () => {
      logger.log('Payload:', payload);
      logger.log('Timestamp:', new Date().toISOString());
    });
  }
};

// Export default for convenience
export default logger;
