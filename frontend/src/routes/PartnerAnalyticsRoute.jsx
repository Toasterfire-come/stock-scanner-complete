import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/SecureAuthContext';
import PartnerAnalytics from '../pages/app/PartnerAnalytics';

/**
 * Protected route for partner analytics
 * Only accessible by whitelisted partner emails:
 * - hamzashehata3000@gmail.com
 */

const PARTNER_EMAILS = [
  'hamzashehata3000@gmail.com',
  // Add more partner emails as needed
];

export default function PartnerAnalyticsRoute() {
  const { user, loading } = useAuth();

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Check authentication
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user email is whitelisted for partner analytics
  const userEmail = (user.email || '').toLowerCase().trim();
  const isPartner = PARTNER_EMAILS.includes(userEmail);

  if (!isPartner) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
          <p className="text-muted-foreground">
            You don't have permission to access partner analytics.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Contact support if you believe this is an error.
          </p>
        </div>
      </div>
    );
  }

  // Render analytics dashboard for authorized partners
  return <PartnerAnalytics />;
}
