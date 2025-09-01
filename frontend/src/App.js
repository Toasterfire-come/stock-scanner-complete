import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "sonner";

// Layouts
import AppLayout from "./layouts/AppLayout";
import AuthLayout from "./layouts/AuthLayout";

// Auth Pages
import SignIn from "./pages/auth/SignIn";
import SignUp from "./pages/auth/SignUp";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";
import OAuthCallback from "./pages/auth/OAuthCallback";
import TwoFactorAuth from "./pages/auth/TwoFactorAuth";

// Onboarding
import OnboardingWizard from "./pages/onboarding/OnboardingWizard";

// Public Pages
import Home from "./pages/Home";
import Pricing from "./pages/Pricing";
import CheckoutSuccess from "./pages/billing/CheckoutSuccess";
import CheckoutFailure from "./pages/billing/CheckoutFailure";

// App Pages
import AppDashboard from "./pages/app/AppDashboard";
import Markets from "./pages/app/Markets";
import StockDetail from "./pages/app/StockDetail";
import Stocks from "./pages/app/Stocks";
import Portfolio from "./pages/app/Portfolio";
import Watchlists from "./pages/app/Watchlists";
import WatchlistDetail from "./pages/app/WatchlistDetail";

// Screener Suite
import ScreenerLibrary from "./pages/app/screeners/ScreenerLibrary";
import CreateScreener from "./pages/app/screeners/CreateScreener";
import EditScreener from "./pages/app/screeners/EditScreener";
import ScreenerResults from "./pages/app/screeners/ScreenerResults";
import Templates from "./pages/app/Templates";

// Market Overview
import MarketHeatmap from "./pages/app/MarketHeatmap";
import SectorsIndustries from "./pages/app/SectorsIndustries";
import TopMovers from "./pages/app/TopMovers";
import PreAfterMarket from "./pages/app/PreAfterMarket";
import EconomicCalendar from "./pages/app/EconomicCalendar";

// News
import NewsFeed from "./pages/app/NewsFeed";
import NewsPreferences from "./pages/app/NewsPreferences";
import NewsSubscribe from "./pages/app/NewsSubscribe";

// Alerts & Signals
import Alerts from "./pages/app/Alerts";
import AlertHistory from "./pages/app/AlertHistory";

// Account Pages
import Profile from "./pages/account/Profile";
import ChangePassword from "./pages/account/ChangePassword";
import NotificationSettings from "./pages/account/NotificationSettings";
import BillingHistory from "./pages/account/BillingHistory";
import CurrentPlan from "./pages/account/CurrentPlan";

// System Pages
import EndpointStatus from "./pages/system/EndpointStatus";

// Content & Docs
import LegalTerms from "./pages/LegalTerms";
import LegalPrivacy from "./pages/LegalPrivacy";
import Docs from "./pages/docs/Docs";

// Mobile
import MobileDashboard from "./pages/mobile/MobileDashboard";

// Error Boundary & Net Indicator
import SystemErrorBoundary from "./components/SystemErrorBoundary";
import LatencyIndicator from "./components/LatencyIndicator";

// Placeholder component for missing pages
const PlaceholderPage = ({ title }) => (
  <div className="container mx-auto px-4 py-8">
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
      <p className="text-gray-600">This page is under development.</p>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <LatencyIndicator />
        <SystemErrorBoundary>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Auth Routes */}
              <Route element={<AuthLayout />}>
                <Route path="/auth/sign-in" element={<SignIn />} />
                <Route path="/auth/sign-up" element={<SignUp />} />
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
                <Route path="/pricing" element={<Pricing />} />

                {/* Marketing Pages - Using placeholders */}
                <Route path="/features" element={<PlaceholderPage title="Features" />} />
                <Route path="/product" element={<PlaceholderPage title="Product" />} />
                <Route path="/data" element={<PlaceholderPage title="Data Coverage" />} />
                <Route path="/use-cases" element={<PlaceholderPage title="Use Cases" />} />
                <Route path="/changelog" element={<PlaceholderPage title="Changelog" />} />
                <Route path="/about" element={<PlaceholderPage title="About" />} />
                <Route path="/contact" element={<PlaceholderPage title="Contact" />} />
                <Route path="/careers" element={<PlaceholderPage title="Careers" />} />
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
                <Route path="/app/sectors" element={<SectorsIndustries />} />
                <Route path="/app/top-movers" element={<TopMovers />} />
                <Route path="/app/pre-after-market" element={<PreAfterMarket />} />
                <Route path="/app/economic-calendar" element={<EconomicCalendar />} />

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
                <Route path="/docs" element={<Docs />} />

                {/* Legal */}
                <Route path="/legal/terms" element={<LegalTerms />} />
                <Route path="/legal/privacy" element={<LegalPrivacy />} />
              </Route>

              {/* Mobile Routes */}
              <Route path="/m/dashboard" element={<MobileDashboard />} />
              <Route path="/m/alerts" element={<Alerts />} />
              <Route path="/m/quick-scan" element={<TopMovers />} />

              {/* Default redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster position="top-right" />
          </div>
        </SystemErrorBoundary>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;