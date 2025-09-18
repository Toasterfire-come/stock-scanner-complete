import React from "react";
import "./App.css";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
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
import Features from "./pages/Features";
import About from "./pages/About";
import Contact from "./pages/Contact";
import PricingPro from "./pages/PricingPro";
import Pricing from "./pages/Pricing";
import AdvancedAnalytics from "./components/AdvancedAnalytics";
import ReferralSystem from "./components/ReferralSystem";
import CheckoutSuccess from "./pages/billing/CheckoutSuccess";
import CheckoutFailure from "./pages/billing/CheckoutFailure";

// App Pages
import ReactLazy from 'react';
const AppDashboard = React.lazy(() => import("./pages/app/AppDashboard"));
const Markets = React.lazy(() => import("./pages/app/Markets"));
const StockDetail = React.lazy(() => import("./pages/app/StockDetail"));
const Stocks = React.lazy(() => import("./pages/app/Stocks"));
const Portfolio = React.lazy(() => import("./pages/app/Portfolio"));
const Watchlists = React.lazy(() => import("./pages/app/Watchlists"));
const WatchlistDetail = React.lazy(() => import("./pages/app/WatchlistDetail"));

// Screener Suite
const ScreenerLibrary = React.lazy(() => import("./pages/app/screeners/ScreenerLibrary"));
const CreateScreener = React.lazy(() => import("./pages/app/screeners/CreateScreener"));
const EditScreener = React.lazy(() => import("./pages/app/screeners/EditScreener"));
const ScreenerResults = React.lazy(() => import("./pages/app/screeners/ScreenerResults"));
const Templates = React.lazy(() => import("./pages/app/Templates"));

// Market Overview
const MarketHeatmap = React.lazy(() => import("./pages/app/MarketHeatmap"));
const SectorsIndustries = React.lazy(() => import("./pages/app/SectorsIndustries"));
const TopMovers = React.lazy(() => import("./pages/app/TopMovers"));
const PreAfterMarket = React.lazy(() => import("./pages/app/PreAfterMarket"));
const EconomicCalendar = React.lazy(() => import("./pages/app/EconomicCalendar"));

// News
const NewsFeed = React.lazy(() => import("./pages/app/NewsFeed"));
const NewsPreferences = React.lazy(() => import("./pages/app/NewsPreferences"));
const NewsSubscribe = React.lazy(() => import("./pages/app/NewsSubscribe"));

// Alerts & Signals
const Alerts = React.lazy(() => import("./pages/app/Alerts"));
const AlertHistory = React.lazy(() => import("./pages/app/AlertHistory"));

// Account Pages
const Profile = React.lazy(() => import("./pages/account/Profile"));
const ChangePassword = React.lazy(() => import("./pages/account/ChangePassword"));
const NotificationSettings = React.lazy(() => import("./pages/account/NotificationSettings"));
const BillingHistory = React.lazy(() => import("./pages/account/BillingHistory"));
const CurrentPlan = React.lazy(() => import("./pages/account/CurrentPlan"));

// System Pages
const EndpointStatus = React.lazy(() => import("./pages/system/EndpointStatus"));

// Content & Docs
import LegalTerms from "./pages/LegalTerms";
import LegalPrivacy from "./pages/LegalPrivacy";
import Documentation from "./pages/docs/Documentation";
import EnterpriseContact from "./pages/EnterpriseContact";

// Marketing Pages
import * as Marketing from "./pages/Marketing";

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
      <HashRouter>
        <LatencyIndicator />
        <SystemErrorBoundary>
          <div className="min-h-screen bg-background">
            <React.Suspense fallback={<div className="p-8 text-center text-gray-600">Loading…</div>}>
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
                <Route path="/features" element={<Features />} />
                <Route path="/about" element={<About />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/pricing" element={<PricingPro />} />
                <Route path="/pricing-old" element={<Pricing />} />
                <Route path="/app/analytics" element={<AdvancedAnalytics />} />
                <Route path="/app/referrals" element={<ReferralSystem />} />

                {/* Marketing Pages - Now using real components */}
                <Route path="/product" element={<Marketing.Product />} />
                <Route path="/data" element={<Marketing.DataCoverage />} />
                <Route path="/use-cases" element={<Marketing.UseCases />} />
                <Route path="/changelog" element={<Marketing.Changelog />} />
                <Route path="/help" element={<Marketing.Help />} />
                <Route path="/help/faq" element={<Marketing.FAQ />} />
                <Route path="/enterprise" element={<EnterpriseContact />} />

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
                <Route path="/docs" element={<Documentation />} />

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
            </React.Suspense>
            <Toaster position="top-right" />
          </div>
        </SystemErrorBoundary>
      </HashRouter>
    </AuthProvider>
  );
}

export default App;