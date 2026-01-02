import React, { useEffect, useState } from 'react';
import subscriptionService from '../utils';
import './SubscriptionSuccess.css';

/**
 * SubscriptionSuccess Page
 * Displayed after user approves subscription on PayPal
 * Shows subscription activation status
 */
const SubscriptionSuccess = () => {
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Wait a moment for webhook to process, then check status
    const checkSubscription = async () => {
      try {
        // Wait 2 seconds for webhook to activate subscription
        await new Promise(resolve => setTimeout(resolve, 2000));

        const result = await subscriptionService.getSubscriptionStatus();

        if (result.success) {
          setSubscription(result);
        } else {
          setError(result.error || 'Failed to retrieve subscription status');
        }
      } catch (err) {
        setError('An error occurred while checking your subscription');
      } finally {
        setLoading(false);
      }
    };

    checkSubscription();
  }, []);

  const getPlanDisplayName = (planTier) => {
    const names = {
      basic: 'Basic',
      pro: 'Pro',
      pay_per_use: 'Pay-Per-Use'
    };
    return names[planTier] || planTier;
  };

  if (loading) {
    return (
      <div className="subscription-success-page">
        <div className="success-container">
          <div className="loading-spinner-large"></div>
          <h1>Activating Your Subscription...</h1>
          <p>Please wait while we confirm your payment with PayPal.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="subscription-success-page">
        <div className="success-container error">
          <div className="icon-error">⚠️</div>
          <h1>Subscription Status Unknown</h1>
          <p>{error}</p>
          <p>
            Don't worry! Your payment is being processed. Please check your email for
            confirmation or visit your account page to view your subscription status.
          </p>
          <div className="action-buttons">
            <a href="/account" className="btn btn-primary">
              Go to Account
            </a>
            <a href="/pricing" className="btn btn-secondary">
              Back to Pricing
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="subscription-success-page">
      <div className="success-container">
        <div className="icon-success">✓</div>
        <h1>Welcome to {getPlanDisplayName(subscription.plan_tier)}!</h1>
        <p className="success-subtitle">
          Your subscription has been activated successfully.
        </p>

        <div className="subscription-details">
          <div className="detail-row">
            <span className="label">Plan:</span>
            <span className="value">{getPlanDisplayName(subscription.plan_tier)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Billing Cycle:</span>
            <span className="value">
              {subscription.billing_cycle === 'monthly' ? 'Monthly' : 'Annual'}
            </span>
          </div>
          <div className="detail-row">
            <span className="label">Status:</span>
            <span className="value status-active">Active</span>
          </div>
          {subscription.current_period_end && (
            <div className="detail-row">
              <span className="label">Next Billing Date:</span>
              <span className="value">
                {new Date(subscription.current_period_end).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>

        <div className="next-steps">
          <h2>What's Next?</h2>
          <ul>
            <li>Start creating advanced screeners and alerts</li>
            <li>Access real-time market data and analytics</li>
            <li>Explore TradingView Premium charting</li>
            <li>Join our community of traders</li>
          </ul>
        </div>

        <div className="action-buttons">
          <a href="/dashboard" className="btn btn-primary">
            Go to Dashboard
          </a>
          <a href="/account" className="btn btn-secondary">
            Manage Subscription
          </a>
        </div>

        <div className="help-text">
          <p>
            You can manage your subscription, update payment methods, or cancel anytime
            from your <a href="/account">account settings</a> or directly in your PayPal account.
          </p>
          <p>
            Need help? <a href="/support">Contact our support team</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionSuccess;
