/**
 * PayPal Subscription Service
 * Handles subscription creation, cancellation, and status management
 */

// Prefer same-origin by default ("/api" is proxied by nginx in Docker, and by setupProxy.js in dev).
const API_URL = (process.env.REACT_APP_BACKEND_URL || '').trim().replace(/\/$/, '') || '';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = () => {
  const token = localStorage.getItem('authToken') || localStorage.getItem('token');
  return token;
};

/**
 * Create a PayPal subscription
 * @param {string} planType - 'basic', 'pro', or 'pay_per_use'
 * @param {string} billingCycle - 'monthly' or 'annual'
 * @returns {Promise<{success: boolean, approval_url?: string, subscription_id?: string, error?: string}>}
 */
export const createSubscription = async (planType, billingCycle) => {
  try {
    const token = getAuthToken();

    if (!token) {
      return {
        success: false,
        error: 'Authentication required. Please log in first.'
      };
    }

    const response = await fetch(`${API_URL}/api/billing/subscription/paypal/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        plan_type: planType,
        billing_cycle: billingCycle
      })
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to create subscription'
      };
    }

    return data;
  } catch (error) {
    console.error('Error creating subscription:', error);
    return {
      success: false,
      error: error.message || 'Network error. Please try again.'
    };
  }
};

/**
 * Get current subscription status
 * @returns {Promise<{success: boolean, plan_tier?: string, status?: string, error?: string}>}
 */
export const getSubscriptionStatus = async () => {
  try {
    const token = getAuthToken();

    if (!token) {
      return {
        success: true,
        plan_tier: 'free',
        status: 'none'
      };
    }

    const response = await fetch(`${API_URL}/api/billing/subscription/paypal/status/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to get subscription status'
      };
    }

    return data;
  } catch (error) {
    console.error('Error getting subscription status:', error);
    return {
      success: false,
      error: error.message || 'Network error. Please try again.'
    };
  }
};

/**
 * Cancel current subscription
 * @returns {Promise<{success: boolean, message?: string, error?: string}>}
 */
export const cancelSubscription = async () => {
  try {
    const token = getAuthToken();

    if (!token) {
      return {
        success: false,
        error: 'Authentication required. Please log in first.'
      };
    }

    const response = await fetch(`${API_URL}/api/billing/subscription/paypal/cancel/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || 'Failed to cancel subscription'
      };
    }

    return data;
  } catch (error) {
    console.error('Error cancelling subscription:', error);
    return {
      success: false,
      error: error.message || 'Network error. Please try again.'
    };
  }
};

/**
 * Handle subscription creation and redirect to PayPal
 * @param {string} planType - 'basic', 'pro', or 'pay_per_use'
 * @param {string} billingCycle - 'monthly' or 'annual'
 */
export const subscribeAndRedirect = async (planType, billingCycle) => {
  try {
    const result = await createSubscription(planType, billingCycle);

    if (result.success && result.approval_url) {
      // Redirect to PayPal for approval
      window.location.href = result.approval_url;
    } else {
      // Handle error
      alert(result.error || 'Failed to create subscription');
      return false;
    }
  } catch (error) {
    console.error('Error in subscribeAndRedirect:', error);
    alert('An error occurred. Please try again.');
    return false;
  }
};

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  const token = getAuthToken();
  return !!token;
};

/**
 * Get plan display name
 * @param {string} planType - 'basic', 'pro', 'pay_per_use', 'free'
 * @returns {string}
 */
export const getPlanDisplayName = (planType) => {
  const names = {
    'free': 'Free',
    'basic': 'Basic',
    'pro': 'Pro',
    'pay_per_use': 'Pay-Per-Use',
    // Legacy support
    'bronze': 'Basic',
    'silver': 'Pro',
    'gold': 'Pay-Per-Use'
  };

  return names[planType] || planType;
};

/**
 * Get plan pricing
 * @param {string} planType - 'basic', 'pro', 'pay_per_use'
 * @param {string} billingCycle - 'monthly' or 'annual'
 * @returns {{price: number, display: string}}
 */
export const getPlanPrice = (planType, billingCycle) => {
  const pricing = {
    basic: {
      monthly: { price: 9.99, display: '$9.99/month' },
      annual: { price: 101.99, display: '$101.99/year' }
    },
    pro: {
      monthly: { price: 24.99, display: '$24.99/month' },
      annual: { price: 254.99, display: '$254.99/year' }
    },
    pay_per_use: {
      monthly: { price: 24.99, display: '$24.99/month + usage' },
      annual: { price: 254.99, display: '$254.99/year + usage' }
    }
  };

  return pricing[planType]?.[billingCycle] || { price: 0, display: 'N/A' };
};

export default {
  createSubscription,
  getSubscriptionStatus,
  cancelSubscription,
  subscribeAndRedirect,
  isAuthenticated,
  getPlanDisplayName,
  getPlanPrice
};
