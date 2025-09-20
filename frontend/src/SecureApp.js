import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";

// Security and Core Providers
import SecurityProvider from "./components/SecurityProvider";
import { AuthProvider } from "./context/SecureAuthContext";
import { BackendStatusProvider, useBackendStatus } from "./context/BackendStatusContext";

// Layouts
import { Suspense, lazy } from 'react';
import AppLayout from "./layouts/AppLayout.js";
import AuthLayout from "./layouts/AuthLayout";

// Auth Pages (force .jsx to prefer the newer components)
const SignIn = lazy(() => import("./pages/auth/SignIn.jsx"));
const SignUp = lazy(() => import("./pages/auth/SignUp.jsx"));
const PlanSelection = lazy(() => import("./pages/auth/PlanSelection"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const VerifyEmail = lazy(() => import("./pages/auth/VerifyEmail"));
const OAuthCallback = lazy(() => import("./pages/auth/OAuthCallback"));
const TwoFactorAuth = lazy(() => import("./pages/auth/TwoFactorAuth"));

// Onboarding
import OnboardingWizard from "./pages/onboarding/OnboardingWizard";

// Public Pages
const Home = lazy(() => import("./pages/Home"));
const Features = lazy(() => import("./pages/Features"));
const About = lazy(() => import("./pages/About"));
const Contact = lazy(() => import("./pages/Contact"));
const PricingPro = lazy(() => import("./pages/PricingPro"));
const Pricing = lazy(() => import("./pages/Pricing"));
const AdvancedAnalytics = lazy(() => import("./components/AdvancedAnalytics"));
const ReferralSystem = lazy(() => import("./components/ReferralSystem"));
const CheckoutSuccess = lazy(() => import("./pages/billing/CheckoutSuccess"));
const CheckoutFailure = lazy(() => import("./pages/billing/CheckoutFailure"));

// App Pages
const AppDashboard = lazy(() => import("./pages/app/AppDashboard"));
const Markets = lazy(() => import("./pages/app/Markets"));
const StockDetail = lazy(() => import("./pages/app/StockDetail"));
const Stocks = lazy(() => import("./pages/app/Stocks"));
const Portfolio = lazy(() => import("./pages/app/Portfolio"));
const Watchlists = lazy(() => import("./pages/app/Watchlists"));
const WatchlistDetail = lazy(() => import("./pages/app/WatchlistDetail"));

// Screener Suite
const ScreenerLibrary = lazy(() => import(/* webpackChunkName: "screeners" */ "./pages/app/screeners/ScreenerLibrary"));
const CreateScreener = lazy(() => import(/* webpackChunkName: "screeners" */ "./pages/app/screeners/CreateScreener"));
const EditScreener = lazy(() => import(/* webpackChunkName: "screeners" */ "./pages/app/screeners/EditScreener"));
const ScreenerResults = lazy(() => import(/* webpackChunkName: "screeners" */ "./pages/app/screeners/ScreenerResults"));
const Templates = lazy(() => import("./pages/app/Templates"));

// Market Overview
const MarketHeatmap = lazy(() => import("./pages/app/MarketHeatmap"));
const TopMovers = lazy(() => import("./pages/app/TopMovers"));

// News
const NewsFeed = lazy(() => import("./pages/app/NewsFeed"));
const NewsPreferences = lazy(() => import("./pages/app/NewsPreferences"));
const NewsSubscribe = lazy(() => import("./pages/app/NewsSubscribe"));

// Alerts & Signals
const Alerts = lazy(() => import("./pages/app/Alerts"));
const AlertHistory = lazy(() => import("./pages/app/AlertHistory"));

// Account Pages
const Profile = lazy(() => import(/* webpackChunkName: "account" */ "./pages/account/Profile"));
const ChangePassword = lazy(() => import(/* webpackChunkName: "account" */ "./pages/account/ChangePassword"));
const NotificationSettings = lazy(() => import(/* webpackChunkName: "account" */ "./pages/account/NotificationSettings"));
const BillingHistory = lazy(() => import(/* webpackChunkName: "account" */ "./pages/account/BillingHistory"));
const CurrentPlan = lazy(() => import(/* webpackChunkName: "account" */ "./pages/account/CurrentPlan"));

// System Pages
const EndpointStatus = lazy(() => import("./pages/system/EndpointStatus"));

// Content & Docs
const LegalTerms = lazy(() => import("./pages/LegalTerms"));
const LegalPrivacy = lazy(() => import("./pages/LegalPrivacy"));
const Documentation = lazy(() => import("./pages/docs/DocumentationSimple"));
const EnterpriseContact = lazy(() => import("./pages/EnterpriseContact"));

// Error Boundary & Components
import SystemErrorBoundary from "./components/SystemErrorBoundary";
import LatencyIndicator from "./components/LatencyIndicator";

// Security utilities
import { logClientError } from "./lib/security";

// Placeholder component for missing pages
const PlaceholderPage = ({ title }) => (
  <div className="container mx-auto px-4 py-16">
    <div className="max-w-2xl mx-auto text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">{title}</h1>
      <p className="text-gray-600 mb-6">We're putting the finishing touches on this section to make sure it meets our quality bar.</p>
      <div className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-blue-600 text-white">
        Back to Home
      </div>
    </div>
  </div>
);

// Offline/Backend Status Banner
const StatusBanner = () => {
  const { isBackendUp } = useBackendStatus();
  
  if (isBackendUp) return null;
  
  return (
    <div className="w-full bg-red-600 text-white text-center text-sm py-2 z-50">
      ⚠️ Backend temporarily unavailable. Some actions are disabled.
    </div>
  );
};

// Main App Component with Security Enhancements
function SecureApp() {
  // Global error handler
  React.useEffect(() => {
    const handleError = (event) => {
      logClientError({
        message: event.error?.message || 'Unknown error',
        stack: event.error?.stack,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        type: 'javascript_error'
      });
    };

    const handleUnhandledRejection = (event) => {
      logClientError({
        message: event.reason?.message || 'Unhandled promise rejection',
        stack: event.reason?.stack,
        type: 'unhandled_promise_rejection'
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return (
    <SecurityProvider>
      <BackendStatusProvider>
        <AuthProvider>
          <BrowserRouter>
            <LatencyIndicator />
            <SystemErrorBoundary>
              <div className="min-h-screen bg-background">
                <StatusBanner />
                <Suspense fallback={<div className="p-8 text-center animate-pulse">
                  <div className="mx-auto h-6 w-40 bg-gray-200 rounded mb-4" />
                  <div className="mx-auto h-4 w-64 bg-gray-100 rounded" />
                </div>}>
                <Routes>
                  {/* Auth Routes */}
                  <Route element={<AuthLayout />}>
                    <Route path="/auth/sign-in" element={<SignIn />} />
                    <Route path="/auth/sign-up" element={<SignUp />} />
                    <Route path="/auth/plan-selection" element={<PlanSelection />} />
                    <Route path="/auth/forgot-password" element={<ForgotPassword />} />
                    <Route path="/auth/reset-password" element={<ResetPassword />} />
                    <Route path="/auth/verify-email" element={<VerifyEmail />} />
                    <Route path="/auth/oauth-callback" element={<OAuthCallback />} />
                    <Route path="/auth/2fa" element={<TwoFactorAuth />} />
                  </Route>

                  {/* Onboarding */}
                  <Route path="/onboarding" element={<OnboardingWizard />} />

                  {/* Billing Routes */}
                  <Route path="/checkout/success" element={<CheckoutSuccess />} />
                  <Route path="/checkout/failure" element={<CheckoutFailure />} />

                  {/* Main App Routes */}
                  <Route element={<AppLayout />}>
                    {/* Public Routes */}
                    <Route path="/" element={<Home />} />
                    <Route path="/features" element={<Features />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/contact" element={<Contact />} />
                    <Route path="/pricing" element={<PricingPro />} />
                    <Route path="/pricing-old" element={<Pricing />} />
                    <Route path="/app/analytics" element={<AdvancedAnalytics />} />
                    <Route path="/app/referrals" element={<ReferralSystem />} />

                    {/* Marketing Pages - Using placeholders */}
                    <Route path="/product" element={<PlaceholderPage title="Product" />} />
                    <Route path="/data" element={<PlaceholderPage title="Data Coverage" />} />
                    <Route path="/use-cases" element={<PlaceholderPage title="Use Cases" />} />
                    <Route path="/changelog" element={<PlaceholderPage title="Changelog" />} />
                    <Route path="/help" element={<PlaceholderPage title="Help" />} />
                    <Route path="/help/faq" element={<PlaceholderPage title="FAQ" />} />

                    {/* App Routes */}
                    <Route path="/app/dashboard" element={<AppDashboard />} />
                    <Route path="/app/markets" element={<Markets />} />
                    <Route path="/app/stocks" element={<Stocks />} />
                    <Route path="/app/stocks/:symbol" element={<StockDetail />} />
                    <Route path="/app/portfolio" element={<Portfolio />} />

                    {/* Screener Suite */}
                    <Route path="/app/screeners" element={<ScreenerLibrary />} />
                    <Route path="/app/screeners/new" element={<CreateScreener />} />
                    <Route path="/app/screeners/:id/edit" element={<EditScreener />} />
                    <Route path="/app/screeners/:id/results" element={<ScreenerResults />} />
                    <Route path="/app/templates" element={<Templates />} />

                    {/* Market Overview */}
                    <Route path="/app/market-heatmap" element={<MarketHeatmap />} />
                    <Route path="/app/top-movers" element={<TopMovers />} />

                    {/* News */}
                    <Route path="/app/news" element={<NewsFeed />} />
                    <Route path="/app/news/preferences" element={<NewsPreferences />} />
                    <Route path="/app/news/subscribe" element={<NewsSubscribe />} />

                    {/* Alerts & Signals */}
                    <Route path="/app/alerts" element={<Alerts />} />
                    <Route path="/app/alerts/history" element={<AlertHistory />} />

                    {/* Watchlists */}
                    <Route path="/app/watchlists" element={<Watchlists />} />
                    <Route path="/app/watchlists/:id" element={<WatchlistDetail />} />

                    {/* Account Routes */}
                    <Route path="/account/profile" element={<Profile />} />
                    <Route path="/account/password" element={<ChangePassword />} />
                    <Route path="/account/notifications" element={<NotificationSettings />} />
                    <Route path="/account/billing" element={<BillingHistory />} />
                    <Route path="/account/plan" element={<CurrentPlan />} />

                    {/* System Routes */}
                    <Route path="/endpoint-status" element={<EndpointStatus />} />

                    {/* Docs & Content */}
                    <Route path="/docs" element={<Documentation />} />
                    <Route path="/enterprise" element={<EnterpriseContact />} />

                    {/* Legal */}
                    <Route path="/legal/terms" element={<LegalTerms />} />
                    <Route path="/legal/privacy" element={<LegalPrivacy />} />
                  </Route>

                  {/* Default redirect */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
                </Suspense>
                
                {/* Toast Notifications */}
                <Toaster 
                  position="top-right" 
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: 'hsl(var(--background))',
                      color: 'hsl(var(--foreground))',
                      border: '1px solid hsl(var(--border))',
                    },
                  }}
                />
              </div>
            </SystemErrorBoundary>
          </BrowserRouter>
        </AuthProvider>
      </BackendStatusProvider>
    </SecurityProvider>
  );
}

export default SecureApp;