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

              {/* Screener Suite - Using placeholders */}
              <Route path="/app/screeners" element={<PlaceholderPage title="Screener Library" />} />
              <Route path="/app/screeners/new" element={<PlaceholderPage title="Create Screener" />} />
              <Route path="/app/screeners/:id/edit" element={<PlaceholderPage title="Edit Screener" />} />
              <Route path="/app/screeners/:id/results" element={<PlaceholderPage title="Screener Results" />} />
              <Route path="/app/templates" element={<PlaceholderPage title="Templates" />} />

              {/* Market Overview - Using placeholders */}
              <Route path="/app/market-heatmap" element={<PlaceholderPage title="Market Heatmap" />} />
              <Route path="/app/sectors" element={<PlaceholderPage title="Sectors & Industries" />} />
              <Route path="/app/top-movers" element={<PlaceholderPage title="Top Movers" />} />
              <Route path="/app/pre-after-market" element={<PlaceholderPage title="Pre/After Market" />} />
              <Route path="/app/economic-calendar" element={<PlaceholderPage title="Economic Calendar" />} />

              {/* News - Using placeholders */}
              <Route path="/app/news" element={<PlaceholderPage title="News Feed" />} />
              <Route path="/app/news/preferences" element={<PlaceholderPage title="News Preferences" />} />
              <Route path="/app/news/subscribe" element={<PlaceholderPage title="News Subscribe" />} />

              {/* Alerts & Signals - Using placeholders */}
              <Route path="/app/alerts" element={<PlaceholderPage title="Alerts" />} />
              <Route path="/app/alerts/history" element={<PlaceholderPage title="Alert History" />} />
              <Route path="/app/signals" element={<PlaceholderPage title="Signal Feed" />} />

              {/* Watchlists */}
              <Route path="/app/watchlists" element={<Watchlists />} />
              <Route path="/app/watchlists/:id" element={<PlaceholderPage title="Watchlist Detail" />} />

              {/* Account Routes */}
              <Route path="/account/profile" element={<Profile />} />
              <Route path="/account/password" element={<ChangePassword />} />
              <Route path="/account/notifications" element={<NotificationSettings />} />
              <Route path="/account/billing" element={<BillingHistory />} />
              <Route path="/account/plan" element={<CurrentPlan />} />

              {/* System Routes */}
              <Route path="/endpoint-status" element={<EndpointStatus />} />

              {/* Content & Docs - Using placeholders */}
              <Route path="/docs" element={<PlaceholderPage title="Documentation" />} />
              <Route path="/blog" element={<PlaceholderPage title="Blog" />} />
              <Route path="/guides" element={<PlaceholderPage title="Guides" />} />
              <Route path="/tutorials" element={<PlaceholderPage title="Tutorials" />} />
              <Route path="/community" element={<PlaceholderPage title="Community" />} />
              <Route path="/roadmap" element={<PlaceholderPage title="Roadmap" />} />

              {/* Legal */}
              <Route path="/legal/terms" element={<LegalTerms />} />
              <Route path="/legal/privacy" element={<LegalPrivacy />} />
            </Route>

            {/* Mobile Routes - Using placeholders */}
            <Route path="/m/dashboard" element={<PlaceholderPage title="Mobile Dashboard" />} />
            <Route path="/m/alerts" element={<PlaceholderPage title="Mobile Alerts" />} />
            <Route path="/m/quick-scan" element={<PlaceholderPage title="Mobile Quick Scan" />} />

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