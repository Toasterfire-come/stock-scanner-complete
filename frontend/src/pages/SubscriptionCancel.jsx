import React from 'react';
import './SubscriptionCancel.css';

/**
 * SubscriptionCancel Page
 * Displayed when user cancels the subscription flow on PayPal
 */
const SubscriptionCancel = () => {
  return (
    <div className="subscription-cancel-page">
      <div className="cancel-container">
        <div className="icon-cancel">⚠️</div>

        <h1>Subscription Cancelled</h1>

        <p className="cancel-subtitle">
          You cancelled the subscription process. No charges have been made to your account.
        </p>

        <div className="info-box">
          <h2>What Happened?</h2>
          <p>
            You were redirected back from PayPal without completing the subscription.
            Your account remains on the free plan with no changes.
          </p>
        </div>

        <div className="action-section">
          <h3>What Would You Like to Do?</h3>

          <div className="action-buttons">
            <a href="/pricing" className="btn btn-primary">
              View Pricing Again
            </a>
            <a href="/dashboard" className="btn btn-secondary">
              Continue with Free Plan
            </a>
          </div>
        </div>

        <div className="help-section">
          <h3>Need Help?</h3>
          <p>
            If you encountered an issue during checkout or have questions about our plans:
          </p>
          <ul>
            <li>
              <a href="/support">Contact our support team</a> - We're here to help
            </li>
            <li>
              <a href="/faq">Check our FAQ</a> - Common questions answered
            </li>
            <li>
              <a href="/pricing">Compare plans</a> - Find the right fit for you
            </li>
          </ul>
        </div>

        <div className="reassurance">
          <p>
            <strong>No worries!</strong> You can subscribe anytime, and we offer a
            14-day money-back guarantee on all paid plans.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionCancel;
