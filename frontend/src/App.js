import React, { useState, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './context/EnhancedAuthContext';
import { useAuth } from './context/EnhancedAuthContext';
import { queryClient, backgroundSync } from './lib/queryClient';
import ErrorBoundary from './components/common/ErrorBoundary';
import PWAInstallBanner from './components/PWAInstallBanner';
import NetworkStatus from './components/NetworkStatus';
import { Loader2 } from 'lucide-react';
import './App.css';

// Lazy load components for better performance
const StockDashboard = React.lazy(() => import('./components/StockDashboard'));
const Login = React.lazy(() => import('./components/Login'));
const Register = React.lazy(() => import('./components/Register'));
const Header = React.lazy(() => import('./components/Header'));

// Loading component
const LoadingSpinner = ({ message = "Loading..." }) => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="text-center">
      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
      <div className="text-gray-600 font-medium">{message}</div>
      <div className="text-gray-400 text-sm mt-1">Please wait...</div>
    </div>
  </div>
);

// Session expired modal
const SessionExpiredModal = ({ onClose, onLogin }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-lg p-6 max-w-md mx-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-2">Session Expired</h2>
      <p className="text-gray-600 mb-4">
        Your session has expired. Please log in again to continue.
      </p>
      <div className="flex gap-3">
        <button
          onClick={onLogin}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Log In Again
        </button>
        <button
          onClick={onClose}
          className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
        >
          Continue as Guest
        </button>
      </div>
    </div>
  </div>
);

// Protected Route component with enhanced error handling
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, sessionExpired, clearSessionExpired } = useAuth();
  
  if (loading) {
    return <LoadingSpinner message="Authenticating..." />;
  }
  
  if (sessionExpired) {
    return (
      <SessionExpiredModal
        onClose={clearSessionExpired}
        onLogin={() => {
          clearSessionExpired();
          window.location.href = '/auth';
        }}
      />
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth" replace />;
};

// Public Route component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner message="Loading application..." />;
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

// Auth page with login/register toggle
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  
  return (
    <ErrorBoundary fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Authentication Error</h2>
          <p className="text-gray-600">Please refresh the page and try again.</p>
        </div>
      </div>
    }>
      {isLogin ? 
        <Login onToggleMode={() => setIsLogin(false)} /> : 
        <Register onToggleMode={() => setIsLogin(true)} />
      }
    </ErrorBoundary>
  );
};

// Main App Layout with network status and PWA features
const AppLayout = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="min-h-screen bg-gray-50">
      <NetworkStatus />
      
      {isAuthenticated && (
        <Suspense fallback={<div className="h-16 bg-white shadow-sm" />}>
          <Header />
        </Suspense>
      )}
      
      <main className={isAuthenticated ? 'pt-0' : ''}>
        {children}
      </main>
      
      <PWAInstallBanner />
    </div>
  );
};

// App component with providers
const App = () => {
  React.useEffect(() => {
    // Start background sync for real-time data
    const cleanup = backgroundSync.start();
    
    // Register service worker for PWA functionality
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then((registration) => {
            console.log('SW registered: ', registration);
          })
          .catch((registrationError) => {
            console.log('SW registration failed: ', registrationError);
          });
      });
    }
    
    // Performance monitoring
    if ('performance' in window && 'getEntriesByType' in performance) {
      // Log performance metrics in development
      if (process.env.NODE_ENV === 'development') {
        setTimeout(() => {
          const navigation = performance.getEntriesByType('navigation')[0];
          console.log('Performance metrics:', {
            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
            totalLoadTime: navigation.loadEventEnd - navigation.fetchStart,
          });
        }, 0);
      }
    }
    
    return cleanup;
  }, []);

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Report to error tracking service in production
        if (process.env.NODE_ENV === 'production') {
          console.error('Global error caught:', { error, errorInfo });
          // TODO: Send to error tracking service (e.g., Sentry)
        }
      }}
    >
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <AppLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  {/* Public routes */}
                  <Route 
                    path="/auth" 
                    element={
                      <PublicRoute>
                        <AuthPage />
                      </PublicRoute>
                    } 
                  />
                  
                  {/* Protected routes */}
                  <Route 
                    path="/dashboard" 
                    element={
                      <ProtectedRoute>
                        <ErrorBoundary>
                          <StockDashboard />
                        </ErrorBoundary>
                      </ProtectedRoute>
                    } 
                  />
                  
                  {/* Default redirect */}
                  <Route 
                    path="/" 
                    element={<Navigate to="/dashboard" replace />} 
                  />
                  
                  {/* Catch all - redirect to dashboard */}
                  <Route 
                    path="*" 
                    element={<Navigate to="/dashboard" replace />} 
                  />
                </Routes>
              </Suspense>
            </AppLayout>
          </BrowserRouter>
        </AuthProvider>
        
        {/* React Query DevTools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;