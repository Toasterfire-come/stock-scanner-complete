/**
 * Quota Limit Interceptor
 *
 * Automatically intercepts fetch responses and dispatches quota limit events
 * when a 429 (Too Many Requests) status is detected.
 *
 * Usage:
 * Import this file in your App.js or index.js to enable global quota monitoring
 */

// Store original fetch
const originalFetch = window.fetch;

// Custom fetch wrapper that checks for quota limits
window.fetch = async (...args) => {
  try {
    const response = await originalFetch(...args);

    // Clone response so we can read it multiple times
    const clonedResponse = response.clone();

    // Check for quota limit (429 status)
    if (clonedResponse.status === 429) {
      try {
        const data = await clonedResponse.json();

        // Dispatch quota limit event
        const event = new CustomEvent('quota-limit-reached', {
          detail: {
            plan: data.plan || data.current_plan || 'basic',
            resource_type: data.resource_type || data.limit_type || 'api_calls',
            current_usage: data.current_usage || data.usage || 0,
            quota_limit: data.quota_limit || data.limit || 0,
            usage_percentage: data.usage_percentage ||
              (data.current_usage && data.quota_limit
                ? Math.round((data.current_usage / data.quota_limit) * 100)
                : 100),
            message: data.message || data.detail || 'Quota limit reached',
            timestamp: new Date().toISOString()
          }
        });

        window.dispatchEvent(event);

        // Log for debugging
        console.warn('[Quota Limit] Detected 429 response:', {
          url: args[0],
          detail: event.detail
        });
      } catch (parseError) {
        // If we can't parse JSON, dispatch generic quota event
        const event = new CustomEvent('quota-limit-reached', {
          detail: {
            plan: 'basic',
            resource_type: 'api_calls',
            current_usage: 0,
            quota_limit: 0,
            usage_percentage: 100,
            message: 'Quota limit reached',
            timestamp: new Date().toISOString()
          }
        });

        window.dispatchEvent(event);

        console.warn('[Quota Limit] Detected 429 response (no JSON):', args[0]);
      }
    }

    return response;
  } catch (error) {
    // Re-throw fetch errors
    throw error;
  }
};

// Export a manual check function for non-fetch APIs
export const checkQuotaLimit = (response) => {
  if (response.status === 429) {
    response.clone().json().then(data => {
      const event = new CustomEvent('quota-limit-reached', {
        detail: {
          plan: data.plan || 'basic',
          resource_type: data.resource_type || 'api_calls',
          current_usage: data.current_usage || 0,
          quota_limit: data.quota_limit || 0,
          usage_percentage: data.usage_percentage || 100,
          message: data.message || 'Quota limit reached',
          timestamp: new Date().toISOString()
        }
      });
      window.dispatchEvent(event);
    }).catch(() => {
      // Generic fallback
      const event = new CustomEvent('quota-limit-reached', {
        detail: {
          plan: 'basic',
          resource_type: 'api_calls',
          current_usage: 0,
          quota_limit: 0,
          usage_percentage: 100,
          message: 'Quota limit reached',
          timestamp: new Date().toISOString()
        }
      });
      window.dispatchEvent(event);
    });
  }
  return response;
};

console.log('[Quota Interceptor] Initialized - monitoring all fetch requests for quota limits');

export default {
  checkQuotaLimit
};
