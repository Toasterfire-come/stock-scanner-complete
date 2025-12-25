import React, { useState, useEffect } from 'react';
import AccessibleButton from './AccessibleButton';

/**
 * Cookie Consent Banner
 * GDPR-compliant cookie consent notice
 * Stores user preference in localStorage
 */
const CookieConsent = () => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if user has already consented
    const hasConsented = localStorage.getItem('cookie_consent');
    if (!hasConsented) {
      // Show banner after 1 second delay
      const timer = setTimeout(() => {
        setShowBanner(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    setShowBanner(false);
  };

  const handleDecline = () => {
    localStorage.setItem('cookie_consent', 'declined');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[9999] bg-white border-t-2 border-gray-200 shadow-2xl"
      role="dialog"
      aria-label="Cookie consent"
      aria-describedby="cookie-consent-description"
    >
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Message */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              We use cookies
            </h3>
            <p
              id="cookie-consent-description"
              className="text-sm text-gray-600 leading-relaxed"
            >
              We use cookies to enhance your browsing experience, analyze site traffic, and personalize content. By clicking "Accept All", you consent to our use of cookies. You can manage your preferences in your account settings.
              {' '}
              <a
                href="/privacy-policy"
                className="text-blue-600 hover:text-blue-800 underline font-medium"
                target="_blank"
                rel="noopener noreferrer"
              >
                Privacy Policy
              </a>
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <AccessibleButton
              variant="ghost"
              onClick={handleDecline}
              ariaLabel="Decline cookies"
              testId="cookie-decline-button"
              className="w-full sm:w-auto"
            >
              Decline
            </AccessibleButton>
            <AccessibleButton
              variant="primary"
              onClick={handleAccept}
              ariaLabel="Accept all cookies"
              testId="cookie-accept-button"
              className="w-full sm:w-auto"
            >
              Accept All
            </AccessibleButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
