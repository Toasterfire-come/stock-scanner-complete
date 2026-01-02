import React, { useState } from 'react';
import { subscribeAndRedirect, isAuthenticated } from '../utils/subscriptionService';
import './SubscriptionButton.css';

/**
 * SubscriptionButton Component
 * Handles subscription creation and redirects to PayPal
 *
 * @param {object} props
 * @param {string} props.planType - 'basic', 'pro', or 'pay_per_use'
 * @param {string} props.billingCycle - 'monthly' or 'annual'
 * @param {string} props.label - Button text (optional)
 * @param {string} props.className - Additional CSS classes (optional)
 * @param {boolean} props.primary - Primary button style (optional)
 */
const SubscriptionButton = ({
  planType,
  billingCycle,
  label,
  className = '',
  primary = false,
  disabled = false
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubscribe = async () => {
    // Check authentication
    if (!isAuthenticated()) {
      alert('Please log in or create an account to subscribe.');
      window.location.href = '/login?redirect=/pricing';
      return;
    }

    // Validate inputs
    if (!planType || !billingCycle) {
      alert('Invalid subscription configuration');
      return;
    }

    setIsLoading(true);

    try {
      await subscribeAndRedirect(planType, billingCycle);
      // If successful, user will be redirected to PayPal
      // If error, subscribeAndRedirect will show alert
    } catch (error) {
      console.error('Subscription error:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getButtonLabel = () => {
    if (label) return label;
    if (isLoading) return 'Processing...';

    const planNames = {
      basic: 'Start Basic',
      pro: 'Start Pro',
      pay_per_use: 'Start Pay-Per-Use'
    };

    return planNames[planType] || 'Subscribe';
  };

  return (
    <button
      className={`subscription-button ${primary ? 'primary' : 'secondary'} ${className}`}
      onClick={handleSubscribe}
      disabled={isLoading || disabled}
    >
      {isLoading && <span className="loading-spinner"></span>}
      {getButtonLabel()}
    </button>
  );
};

export default SubscriptionButton;
