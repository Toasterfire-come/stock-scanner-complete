/**
 * Client-Side Rate Limiter
 * Prevents excessive API calls and improves UX with intelligent throttling
 * MVP2 v3.4 - Production Hardening
 */

class RateLimiter {
  constructor(maxRequests = 100, timeWindow = 60000) {
    /**
     * @param {number} maxRequests - Maximum number of requests allowed in the time window
     * @param {number} timeWindow - Time window in milliseconds (default: 1 minute)
     */
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;

    // Store request timestamps by endpoint
    this.requests = new Map();

    // Store pending requests for debouncing
    this.pending = new Map();

    // Track blocked requests for monitoring
    this.blocked = 0;
  }

  /**
   * Check if a request to an endpoint is allowed
   * @param {string} endpoint - API endpoint (e.g., '/api/stocks/scan/')
   * @returns {boolean} - True if request is allowed
   */
  canMakeRequest(endpoint) {
    const now = Date.now();
    const requestTimestamps = this.requests.get(endpoint) || [];

    // Filter out timestamps outside the time window
    const recentRequests = requestTimestamps.filter(
      (timestamp) => now - timestamp < this.timeWindow
    );

    // Update the map with filtered timestamps
    this.requests.set(endpoint, recentRequests);

    // Check if under the limit
    if (recentRequests.length < this.maxRequests) {
      return true;
    }

    // Rate limit exceeded
    this.blocked++;
    console.warn(
      `Rate limit exceeded for ${endpoint}. ` +
      `${recentRequests.length}/${this.maxRequests} requests in last ${this.timeWindow / 1000}s`
    );
    return false;
  }

  /**
   * Record a request to an endpoint
   * @param {string} endpoint - API endpoint
   */
  recordRequest(endpoint) {
    const now = Date.now();
    const requestTimestamps = this.requests.get(endpoint) || [];
    requestTimestamps.push(now);
    this.requests.set(endpoint, requestTimestamps);
  }

  /**
   * Debounce a request - only execute if not called again within delay
   * @param {string} key - Unique key for the request
   * @param {Function} fn - Function to execute
   * @param {number} delay - Delay in milliseconds (default: 300ms)
   * @returns {Promise} - Promise that resolves with the function result
   */
  debounce(key, fn, delay = 300) {
    return new Promise((resolve, reject) => {
      // Clear existing timeout for this key
      if (this.pending.has(key)) {
        clearTimeout(this.pending.get(key).timeout);
      }

      // Set new timeout
      const timeout = setTimeout(async () => {
        try {
          const result = await fn();
          resolve(result);
          this.pending.delete(key);
        } catch (error) {
          reject(error);
          this.pending.delete(key);
        }
      }, delay);

      this.pending.set(key, { timeout, resolve, reject });
    });
  }

  /**
   * Throttle a request - execute at most once per delay period
   * @param {string} key - Unique key for the request
   * @param {Function} fn - Function to execute
   * @param {number} delay - Minimum delay between executions (default: 1000ms)
   * @returns {Promise|null} - Promise that resolves with the function result, or null if throttled
   */
  throttle(key, fn, delay = 1000) {
    const now = Date.now();
    const lastExecution = this.pending.get(key)?.lastExecution || 0;

    if (now - lastExecution < delay) {
      console.debug(`Throttled request for ${key}. Last execution ${now - lastExecution}ms ago`);
      return null;
    }

    // Update last execution time
    this.pending.set(key, { lastExecution: now });

    // Execute function
    return fn();
  }

  /**
   * Get statistics about rate limiting
   * @returns {Object} - Statistics object
   */
  getStats() {
    let totalRequests = 0;
    const endpointStats = {};

    this.requests.forEach((timestamps, endpoint) => {
      const recent = timestamps.filter(
        (t) => Date.now() - t < this.timeWindow
      );
      endpointStats[endpoint] = {
        recent: recent.length,
        total: timestamps.length,
        limit: this.maxRequests
      };
      totalRequests += recent.length;
    });

    return {
      totalRequests,
      blocked: this.blocked,
      endpoints: endpointStats,
      timeWindow: this.timeWindow,
      maxRequests: this.maxRequests
    };
  }

  /**
   * Reset rate limiter state
   * @param {string} endpoint - Optional endpoint to reset, or all if not specified
   */
  reset(endpoint = null) {
    if (endpoint) {
      this.requests.delete(endpoint);
      console.debug(`Reset rate limiter for ${endpoint}`);
    } else {
      this.requests.clear();
      this.pending.clear();
      this.blocked = 0;
      console.debug('Reset all rate limiters');
    }
  }

  /**
   * Get time until next request is allowed
   * @param {string} endpoint - API endpoint
   * @returns {number} - Milliseconds until next request allowed (0 if allowed now)
   */
  getTimeUntilNextRequest(endpoint) {
    const now = Date.now();
    const requestTimestamps = this.requests.get(endpoint) || [];

    if (requestTimestamps.length < this.maxRequests) {
      return 0;
    }

    // Find the oldest timestamp within the window
    const oldestRelevantTimestamp = requestTimestamps
      .filter((t) => now - t < this.timeWindow)
      .sort((a, b) => a - b)[0];

    if (!oldestRelevantTimestamp) {
      return 0;
    }

    // Calculate time until oldest request expires
    const timeUntilExpiry = this.timeWindow - (now - oldestRelevantTimestamp);
    return Math.max(0, timeUntilExpiry);
  }
}

// Create singleton instances with different limits

// API Rate Limiter - 100 requests per minute per endpoint
export const apiRateLimiter = new RateLimiter(100, 60000);

// Real-time Data Rate Limiter - 30 requests per minute (for expensive operations)
export const realtimeRateLimiter = new RateLimiter(30, 60000);

// Search Rate Limiter - 50 requests per minute (for search/autocomplete)
export const searchRateLimiter = new RateLimiter(50, 60000);

// Export the class for custom instances
export default RateLimiter;

/**
 * Example usage:
 *
 * import { apiRateLimiter } from './utils/rateLimiter';
 *
 * // Before making an API call
 * if (apiRateLimiter.canMakeRequest('/api/stocks/scan/')) {
 *   apiRateLimiter.recordRequest('/api/stocks/scan/');
 *   const response = await axios.get('/api/stocks/scan/');
 * } else {
 *   const waitTime = apiRateLimiter.getTimeUntilNextRequest('/api/stocks/scan/');
 *   console.log(`Rate limit exceeded. Please wait ${waitTime}ms`);
 * }
 *
 * // Debounce search input
 * const handleSearch = (query) => {
 *   searchRateLimiter.debounce('ticker-search', async () => {
 *     const results = await searchTickers(query);
 *     setResults(results);
 *   }, 300);
 * };
 *
 * // Throttle expensive operations
 * const handleChartUpdate = () => {
 *   realtimeRateLimiter.throttle('chart-update', async () => {
 *     await fetchChartData();
 *   }, 2000);
 * };
 */
