import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/SecureAuthContext";
import { Alert, AlertDescription } from "./ui/alert";
import { AlertTriangle, LogIn } from "lucide-react";
import { Button } from "./ui/button";
import { Link } from "react-router-dom";

const ProtectedRoute = ({ children, requireAuth = true }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    // For user pages (/app/*), show access denied message
    if (location.pathname.startsWith('/app')) {
      return (
        <div className="min-h-screen bg-gray-50 p-6">
          <div className="max-w-2xl mx-auto">
            <Alert className="mb-8 border-red-200 bg-red-50">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <AlertDescription className="text-red-800 text-lg">
                <div className="font-semibold mb-2">Access Restricted</div>
                <p className="mb-4">
                  This page is only accessible to signed-in users. You need to sign in or create an account to access app features like Dashboard, Markets, Stocks, Portfolio, Watchlists, Screeners, and Alerts.
                </p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button asChild className="bg-blue-600 hover:bg-blue-700">
                    <Link to="/auth/sign-in" state={{ from: location }}>
                      <LogIn className="h-4 w-4 mr-2" />
                      Sign In
                    </Link>
                  </Button>
                  <Button asChild variant="outline">
                    <Link to="/auth/sign-up" state={{ from: location }}>
                      Create Free Account
                    </Link>
                  </Button>
                </div>
              </AlertDescription>
            </Alert>

            {/* Show some marketing content */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Why Sign Up for Trade Scan Pro?
              </h2>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span>Access real-time market data and stock information</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span>Create and manage custom screeners and watchlists</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span>Set up alerts for price movements and volume changes</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span>Track your portfolio performance with detailed analytics</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span>Get access to professional-grade tools and insights</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      );
    }

    // For other protected routes, redirect to sign-in
    return <Navigate to="/auth/sign-in" state={{ from: location }} replace />;
  }

  // If user is authenticated or authentication is not required, render children
  return children;
};

export default ProtectedRoute;