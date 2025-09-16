import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/SecureAuthContext';
import { Loader2 } from 'lucide-react';

const ProtectedRoute = ({ children, requireAuth = true, redirectTo = '/auth/sign-in' }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    // Give a small delay to allow auth state to settle after login
    if (!isLoading) {
      const timer = setTimeout(() => {
        setShouldRedirect(true);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  // Show loading state while checking authentication
  if (isLoading || !shouldRedirect) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // If authentication is required and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    // Preserve the attempted location for redirecting after login
    const redirectPath = location.pathname + location.search;
    return <Navigate to={`${redirectTo}?redirect=${encodeURIComponent(redirectPath)}`} replace />;
  }

  // If authentication is not required but user is authenticated (for auth pages)
  if (!requireAuth && isAuthenticated) {
    // Redirect authenticated users away from auth pages
    const params = new URLSearchParams(location.search);
    const redirect = params.get('redirect');
    return <Navigate to={redirect || '/app/dashboard'} replace />;
  }

  // Render children if all checks pass
  return children;
};

export default ProtectedRoute;