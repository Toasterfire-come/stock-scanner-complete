/**
 * useQuotaLimit Hook
 *
 * Monitors API responses for quota limit errors (429 status)
 * and triggers the upgrade modal when limits are reached
 */

import { useState, useEffect, useCallback } from 'react';

const useQuotaLimit = () => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [limitData, setLimitData] = useState({
    currentPlan: 'basic',
    resourceType: 'api_calls',
    currentUsage: 0,
    quotaLimit: 0,
    usagePercentage: 100
  });

  // Listen for quota limit events
  useEffect(() => {
    const handleQuotaLimitEvent = (event) => {
      const { detail } = event;
      if (detail) {
        setLimitData({
          currentPlan: detail.plan || 'basic',
          resourceType: detail.resource_type || 'api_calls',
          currentUsage: detail.current_usage || 0,
          quotaLimit: detail.quota_limit || 0,
          usagePercentage: detail.usage_percentage || 100
        });
        setShowUpgradeModal(true);
      }
    };

    window.addEventListener('quota-limit-reached', handleQuotaLimitEvent);

    return () => {
      window.removeEventListener('quota-limit-reached', handleQuotaLimitEvent);
    };
  }, []);

  const closeModal = useCallback(() => {
    setShowUpgradeModal(false);
  }, []);

  const checkResponse = useCallback((response, resourceType = 'api_calls') => {
    // Check if response indicates quota limit reached
    if (response.status === 429) {
      // Try to parse quota info from response
      response.json().then(data => {
        const event = new CustomEvent('quota-limit-reached', {
          detail: {
            plan: data.plan || 'basic',
            resource_type: data.resource_type || resourceType,
            current_usage: data.current_usage || 0,
            quota_limit: data.quota_limit || 0,
            usage_percentage: data.usage_percentage || 100,
            message: data.message || 'Quota limit reached'
          }
        });
        window.dispatchEvent(event);
      }).catch(() => {
        // Fallback if can't parse response
        const event = new CustomEvent('quota-limit-reached', {
          detail: {
            plan: 'basic',
            resource_type: resourceType,
            current_usage: 0,
            quota_limit: 0,
            usage_percentage: 100,
            message: 'Quota limit reached'
          }
        });
        window.dispatchEvent(event);
      });
    }
    return response;
  }, []);

  return {
    showUpgradeModal,
    limitData,
    closeModal,
    checkResponse
  };
};

export default useQuotaLimit;
