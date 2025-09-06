import React, { useState, Suspense, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './context/EnhancedAuthContext';
import { useAuth } from './context/EnhancedAuthContext';
import { queryClient, backgroundSync } from './lib/queryClient';
import ErrorBoundary from './components/common/ErrorBoundary';
import PWAInstallBanner from './components/PWAInstallBanner';
import NetworkStatus, { ConnectionSpeed } from './components/NetworkStatus';
import { Loader2 } from 'lucide-react';
import { Toaster } from 'sonner';
import './App.css';

// Lazy load components for better performance and code splitting
const StockDashboard = React.lazy(() => import('./components/StockDashboard'));
const Login = React.lazy(() => import('./components/Login'));
const Register = React.lazy(() => import('./components/Register'));
const Header = React.lazy(() => import('./components/Header'));

// Enhanced loading component with multiple states
interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Loading...", 
  size = 'md',
  fullScreen = true 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const containerClasses = fullScreen 
    ? 'min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center'
    : 'flex items-center justify-center p-4';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        <div className="relative mb-4">
          <Loader2 className={`${sizeClasses[size]} animate-spin mx-auto text-blue-600`} />
          <div className="absolute inset-0 animate-ping">
            <div className={`${sizeClasses[size]} rounded-full bg-blue-200 opacity-25 mx-auto`} />
          </div>
        </div>
        <div className="text-gray-700 font-medium text-sm sm:text-base">{message}</div>
        <div className="text-gray-500 text-xs sm:text-sm mt-1">Please wait...</div>
        
        {/* Progress dots animation */}
        <div className="flex justify-center mt-3 space-x-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`w-2 h-2 bg-blue-400 rounded-full animate-bounce`}
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

// Enhanced session expired modal with better UX
interface SessionExpiredModalProps {
  onClose: () => void;
  onLogin: () => void;
}

const SessionExpiredModal: React.FC<SessionExpiredModalProps> = ({ onClose, onLogin }) => (
  <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4 transform transition-all">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Session Expired</h2>
        <p className="text-gray-600">
          Your session has expired for security reasons. Please log in again to continue using the app.
        </p>
      </div>
      
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onLogin}
          className="flex-1 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Log In Again
        </button>
        <button
          onClick={onClose}
          className="flex-1 bg-gray-100 text-gray-800 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          Continue as Guest
        </button>
      </div>
      
      <p className="text-xs text-gray-500 text-center mt-4">
        Guest mode has limited functionality
      </p>
    </div>
  </div>
);

// Enhanced protected route with loading states
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading, sessionExpired, clearSessionExpired } = useAuth();
  
  if (loading) {
    return <LoadingSpinner message="Authenticating user..." />;
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
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" replace />;
};

// Enhanced public route with loading states
interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner message="Loading application..." />;
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
};

// Enhanced auth page with better transitions
const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  const handleToggleMode = () => {
    setIsTransitioning(true);
    setTimeout(() => {
      setIsLogin(!isLogin);
      setIsTransitioning(false);
    }, 150);
  };
  
  return (
    <ErrorBoundary fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center bg-white rounded-xl shadow-lg p-8 max-w-md w-full">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Authentication Error</h2>
          <p className="text-gray-600 mb-4">Something went wrong with the authentication system.</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Page
          </button>
        </div>
      </div>
    }>
      <div className={`transition-opacity duration-150 ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
        {isLogin ? 
          <Login onToggleMode={handleToggleMode} /> : 
          <Register onToggleMode={handleToggleMode} />
        }
      </div>
    </ErrorBoundary>
  );
};

// Main app layout with enhanced design
interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Network status indicators */}
      <NetworkStatus />
      <ConnectionSpeed />
      
      {/* Header for authenticated users */}
      {isAuthenticated && (
        <Suspense fallback={
          <div className="h-16 bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200" />
        }>
          <Header />
        </Suspense>
      )}
      
      {/* Main content area */}
      <main className={`transition-all duration-300 ${isAuthenticated ? 'pt-0' : ''}`}>
        <div className="relative">
          {children}
        </div>
      </main>
      
      {/* PWA install banner */}
      <PWAInstallBanner />
      
      {/* Toast notifications */}
      <Toaster 
        position="top-right"
        richColors
        closeButton
        duration={4000}
        toastOptions={{
          style: {
            background: 'white',
            border: '1px solid #e5e7eb',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          }
        }}
      />
    </div>
  );
};

// Main App component with enhanced features
const App: React.FC = () => {
  const [isAppReady, setIsAppReady] = useState(false);
  
  useEffect(() => {
    let cleanup: (() => void) | undefined;

    const initializeApp = async () => {
      try {
        // Start background sync for real-time data
        cleanup = backgroundSync.start();
        
        // Prefetch critical data (will be loaded on-demand by React Query)
        // await Promise.allSettled([
        //   prefetchUtils.prefetchUserProfile(),
        //   prefetchUtils.prefetchTrending(),
        //   prefetchUtils.prefetchPlatformStats(),
        // ]);
        
        // Register service worker for PWA functionality
        if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
          try {
            const registration = await navigator.serviceWorker.register('/sw.js', {
              scope: '/',
              updateViaCache: 'none'
            });
            
            console.log('✅ Service Worker registered successfully:', registration);
            
            // Listen for service worker updates
            registration.addEventListener('updatefound', () => {
              console.log('🔄 Service Worker update found');
            });
            
            // Check for updates immediately and then every 10 minutes
            await registration.update();
            setInterval(() => registration.update(), 10 * 60 * 1000);
            
          } catch (error) {
            console.warn('⚠️ Service Worker registration failed:', error);
          }
        }
        
        // Performance monitoring and analytics
        if (typeof window !== 'undefined' && 'performance' in window) {
          // Log performance metrics in development
          if (process.env.NODE_ENV === 'development') {
            setTimeout(() => {
              const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
              if (navigation) {
                console.log('📊 Performance Metrics:', {
                  domContentLoaded: Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart),
                  loadComplete: Math.round(navigation.loadEventEnd - navigation.loadEventStart),
                  totalLoadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
                  timeToFirstByte: Math.round(navigation.responseStart - navigation.requestStart),
                });
              }
            }, 0);
          }
        }
        
        // Initialize performance observer for Core Web Vitals
        if ('PerformanceObserver' in window) {
          try {
            const observer = new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if (entry.entryType === 'largest-contentful-paint') {
                  console.log('📈 LCP:', Math.round(entry.startTime));
                }
                if (entry.entryType === 'first-input') {
                  const fid = entry as PerformanceEventTiming;
                  if (fid.processingStart) {
                    console.log('⚡ FID:', Math.round(fid.processingStart - fid.startTime));
                  }
                }
              }
            });
            
            observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
          } catch (error) {
            console.warn('Performance Observer not supported:', error);
          }
        }
        
        setIsAppReady(true);
        
      } catch (error) {
        console.error('❌ App initialization failed:', error);
        setIsAppReady(true); // Still show the app even if some features fail
      }
    };

    initializeApp();
    
    return () => {
      cleanup?.();
    };
  }, []);

  // Show loading screen while app initializes
  if (!isAppReady) {
    return <LoadingSpinner message="Initializing Stock Scanner..." size="lg" />;
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // Report to error tracking service in production
        if (process.env.NODE_ENV === 'production') {
          console.error('🚨 Global error caught:', { error, errorInfo });
          // TODO: Send to error tracking service (e.g., Sentry, LogRocket)
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
                  
                  {/* Default redirects */}
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
        
        {/* React Query DevTools - disabled temporarily due to configuration issues */}
        {false && process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools 
            initialIsOpen={false}
          />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;