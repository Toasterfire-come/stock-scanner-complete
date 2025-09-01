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

// Screener Suite (P0)
import ScreenerLibrary from "./pages/app/screeners/ScreenerLibrary";
import CreateScreener from "./pages/app/screeners/CreateScreener";
import EditScreener from "./pages/app/screeners/EditScreener";
import ScreenerResults from "./pages/app/screeners/ScreenerResults";
import Templates from "./pages/app/Templates";

// Market Overview (P0)
import MarketHeatmap from "./pages/app/MarketHeatmap";
import SectorsIndustries from "./pages/app/SectorsIndustries";
import TopMovers from "./pages/app/TopMovers";
import PreAfterMarket from "./pages/app/PreAfterMarket";
import EconomicCalendar from "./pages/app/EconomicCalendar";

// News (P0)
import NewsFeed from "./pages/app/NewsFeed";
import NewsPreferences from "./pages/app/NewsPreferences";
import NewsSubscribe from "./pages/app/NewsSubscribe";

// Account Pages
import Profile from "./pages/account/Profile";
import ChangePassword from "./pages/account/ChangePassword";
import NotificationSettings from "./pages/account/NotificationSettings";
import BillingHistory from "./pages/account/BillingHistory";
import CurrentPlan from "./pages/account/CurrentPlan";

// System Pages
import EndpointStatus from "./pages/system/EndpointStatus";

// Alerts & Signals (P1)
import Alerts from "./pages/app/Alerts";
import AlertHistory from "./pages/app/AlertHistory";
import SignalFeed from "./pages/app/SignalFeed";

// Watchlists (P1)
import Watchlists from "./pages/app/Watchlists";
import WatchlistDetail from "./pages/app/WatchlistDetail";

// Portfolio
import Portfolio from "./pages/app/Portfolio";

// Docs & Content (P1)
import Docs from "./pages/content/Docs";
import Blog from "./pages/content/Blog";
import Guides from "./pages/content/Guides";
import Tutorials from "./pages/content/Tutorials";
import Community from "./pages/content/Community";
import Roadmap from "./pages/content/Roadmap";

// Mobile Routes (P1)
import MobileDashboard from "./pages/mobile/MobileDashboard";
import MobileAlerts from "./pages/mobile/MobileAlerts";
import MobileQuickScan from "./pages/mobile/MobileQuickScan";

// Legal Pages
import LegalTerms from "./pages/legal/LegalTerms";
import LegalPrivacy from "./pages/legal/LegalPrivacy";

// Marketing Pages
import { Features, Product, DataCoverage, UseCases, Changelog, About, Contact, Careers, Help, FAQ } from "./pages/marketing/Marketing";

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