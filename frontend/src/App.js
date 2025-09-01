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

// Account Pages
import Profile from "./pages/account/Profile";
import ChangePassword from "./pages/account/ChangePassword";
import NotificationSettings from "./pages/account/NotificationSettings";
import BillingHistory from "./pages/account/BillingHistory";
import CurrentPlan from "./pages/account/CurrentPlan";

// System Pages
import EndpointStatus from "./pages/system/EndpointStatus";

// Legal Pages
import LegalTerms from "./pages/LegalTerms";
import LegalPrivacy from "./pages/LegalPrivacy";

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
              
              {/* Marketing Pages */}
              <Route path="/features" element={<Features />} />
              <Route path="/product" element={<Product />} />
              <Route path="/data" element={<DataCoverage />} />
              <Route path="/use-cases" element={<UseCases />} />
              <Route path="/changelog" element={<Changelog />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/careers" element={<Careers />} />
              <Route path="/help" element={<Help />} />
              <Route path="/help/faq" element={<FAQ />} />

              {/* App Routes */}
              <Route path="/app/dashboard" element={<AppDashboard />} />
              <Route path="/app/markets" element={<Markets />} />
              <Route path="/app/stocks" element={<Stocks />} />
              <Route path="/app/stocks/:symbol" element={<StockDetail />} />
              <Route path="/app/portfolio" element={<Portfolio />} />

              {/* Screener Suite (P0) */}
              <Route path="/app/screeners" element={<ScreenerLibrary />} />
              <Route path="/app/screeners/new" element={<CreateScreener />} />
              <Route path="/app/screeners/:id/edit" element={<EditScreener />} />
              <Route path="/app/screeners/:id/results" element={<ScreenerResults />} />
              <Route path="/app/templates" element={<Templates />} />

              {/* Market Overview (P0) */}
              <Route path="/app/market-heatmap" element={<MarketHeatmap />} />
              <Route path="/app/sectors" element={<SectorsIndustries />} />
              <Route path="/app/top-movers" element={<TopMovers />} />
              <Route path="/app/pre-after-market" element={<PreAfterMarket />} />
              <Route path="/app/economic-calendar" element={<EconomicCalendar />} />

              {/* News (P0) */}
              <Route path="/app/news" element={<NewsFeed />} />
              <Route path="/app/news/preferences" element={<NewsPreferences />} />
              <Route path="/app/news/subscribe" element={<NewsSubscribe />} />

              {/* Alerts & Signals (P1) */}
              <Route path="/app/alerts" element={<Alerts />} />
              <Route path="/app/alerts/history" element={<AlertHistory />} />
              <Route path="/app/signals" element={<SignalFeed />} />

              {/* Watchlists (P1) */}
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

              {/* Content & Docs (P1) */}
              <Route path="/docs" element={<Docs />} />
              <Route path="/blog" element={<Blog />} />
              <Route path="/guides" element={<Guides />} />
              <Route path="/tutorials" element={<Tutorials />} />
              <Route path="/community" element={<Community />} />
              <Route path="/roadmap" element={<Roadmap />} />

              {/* Legal */}
              <Route path="/legal/terms" element={<LegalTerms />} />
              <Route path="/legal/privacy" element={<LegalPrivacy />} />
            </Route>

            {/* Mobile Routes (P1) */}
            <Route path="/m/dashboard" element={<MobileDashboard />} />
            <Route path="/m/alerts" element={<MobileAlerts />} />
            <Route path="/m/quick-scan" element={<MobileQuickScan />} />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;