import React, { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/SecureAuthContext";
import { Toaster } from "sonner";
import { BackendStatusProvider, useBackendStatus } from "./context/BackendStatusContext";
import { TradingModeProvider } from "./context/TradingModeContext";

// Components
import ProtectedRoute from "./components/ProtectedRoute";

// Layouts
import EnhancedAppLayout from "./layouts/EnhancedAppLayout.jsx";
import AuthLayout from "./layouts/AuthLayout";

// Auth Pages
import SignIn from "./pages/auth/SignIn.jsx";
import SignUp from "./pages/auth/SignUp.jsx";
import PlanSelection from "./pages/auth/PlanSelection";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";
import OAuthCallback from "./pages/auth/OAuthCallback";
// TwoFactorAuth removed

// Onboarding
import OnboardingWizard from "./pages/onboarding/OnboardingWizard";

// Public Pages
import { Suspense, lazy } from "react";
const Home = lazy(() => import(/* webpackPrefetch: true */ "./pages/Home"));
const Features = lazy(() => import(/* webpackPrefetch: true */ "./pages/Features"));
const About = lazy(() => import(/* webpackPrefetch: true */ "./pages/About"));
const Contact = lazy(() => import(/* webpackPrefetch: true */ "./pages/Contact"));
const PricingPro = lazy(() => import(/* webpackPrefetch: true */ "./pages/PricingPro"));
const Pricing = lazy(() => import(/* webpackPrefetch: true */ "./pages/Pricing"));
const StockFilter = lazy(() => import(/* webpackPrefetch: true */ "./pages/StockFilter"));
const MarketScan = lazy(() => import(/* webpackPrefetch: true */ "./pages/MarketScan"));
const DemoScanner = lazy(() => import(/* webpackPrefetch: true */ "./pages/DemoScanner"));
const Resources = lazy(() => import(/* webpackPrefetch: true */ "./pages/Resources"));
const Press = lazy(() => import(/* webpackPrefetch: true */ "./pages/Press"));
const Widgets = lazy(() => import(/* webpackPrefetch: true */ "./pages/Widgets"));
const Badges = lazy(() => import(/* webpackPrefetch: true */ "./pages/Badges"));
const Partners = lazy(() => import(/* webpackPrefetch: true */ "./pages/Partners"));
import AdvancedAnalytics from "./components/AdvancedAnalytics";
import ReferralSystem from "./components/ReferralSystem";
import CheckoutSuccess from "./pages/billing/CheckoutSuccess";
import CheckoutFailure from "./pages/billing/CheckoutFailure";
import Checkout from "./pages/billing/Checkout";

// App Pages (Protected)
const AppDashboard = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/AppDashboard"));
const Markets = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/Markets"));
const StockDetail = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/StockDetail"));
const Stocks = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/Stocks"));
const Portfolio = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/Portfolio"));
const Watchlists = lazy(() => import(/* webpackPrefetch: true */ "./pages/app/Watchlists"));
import WatchlistDetail from "./pages/app/WatchlistDetail";

// Developer Tools (Gold Plan)
import DeveloperDashboard from "./pages/app/developer/DeveloperDashboard";
import ApiKeyManagement from "./pages/app/developer/ApiKeyManagement";
import UsageStatistics from "./pages/app/developer/UsageStatistics";
import ApiDocumentation from "./pages/app/developer/ApiDocumentation";
import DeveloperConsole from "./pages/app/developer/DeveloperConsole";

// Screener Suite (Protected)
import ScreenerLibrary from "./pages/app/screeners/ScreenerLibrary";
import CreateScreener from "./pages/app/screeners/CreateScreener";
import EditScreener from "./pages/app/screeners/EditScreener";
import ScreenerResults from "./pages/app/screeners/ScreenerResults";
import ScreenerDetail from "./pages/app/screeners/ScreenerDetail";
import Templates from "./pages/app/Templates";

// Market Overview (Protected)
import MarketHeatmap from "./pages/app/MarketHeatmap";
import SectorsIndustries from "./pages/app/SectorsIndustries";
import TopMovers from "./pages/app/TopMovers";
import PreAfterMarket from "./pages/app/PreAfterMarket";
import EconomicCalendar from "./pages/app/EconomicCalendar";

// News (Protected)
import NewsFeed from "./pages/app/NewsFeed";
import NewsPreferences from "./pages/app/NewsPreferences";
import NewsSubscribe from "./pages/app/NewsSubscribe";

// Alerts & Signals (Protected)
import Alerts from "./pages/app/Alerts";
import AlertHistory from "./pages/app/AlertHistory";

// Account Pages (Protected)
import Profile from "./pages/account/Profile";
import ChangePassword from "./pages/account/ChangePassword";
import NotificationSettings from "./pages/account/NotificationSettings";
import BillingHistory from "./pages/account/BillingHistory";
import CurrentPlan from "./pages/account/CurrentPlan";
import Settings from "./pages/account/Settings";

// System Pages
import EndpointStatus from "./pages/system/EndpointStatus";

// Content & Docs
import LegalTerms from "./pages/LegalTerms";
import LegalPrivacy from "./pages/LegalPrivacy";
import Documentation from "./pages/docs/Documentation";
import CreateAccount from "./pages/docs/getting-started/CreateAccount";
import Dashboard from "./pages/docs/getting-started/Dashboard";
import FirstScreener from "./pages/docs/getting-started/FirstScreener";
import DocsCategory from "./pages/docs/DocsCategory";
import DocArticle from "./pages/docs/DocArticle";
import EnterpriseContact from "./pages/enterprise/EnterpriseContact";
import Help from "./pages/Help";
import ReferralApply from "./pages/ReferralApply";
import AdminConsole from "./pages/admin/AdminConsole";

// Enterprise Solutions
import QuoteRequest from "./pages/enterprise/QuoteRequest";
import SolutionsShowcase from "./pages/enterprise/SolutionsShowcase";
import WhiteLabelConfig from "./pages/enterprise/WhiteLabelConfig";

// Data Export System
import ExportManager from "./pages/app/exports/ExportManager";
import CustomReportBuilder from "./pages/app/exports/CustomReportBuilder";
import ScheduledExports from "./pages/app/exports/ScheduledExports";
import DownloadHistory from "./pages/app/exports/DownloadHistory";

// Error Boundary & Net Indicator
import SystemErrorBoundary from "./components/SystemErrorBoundary";
// import LatencyIndicator from "./components/LatencyIndicator";
// hotkey for command palette
function useGlobalHotkeys(setCmdOpen) {
  useEffect(() => {
    const onKey = (e) => {
      const isK = e.key?.toLowerCase() === 'k';
      if ((e.ctrlKey || e.metaKey) && isK) {
        e.preventDefault();
        setCmdOpen(true);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [setCmdOpen]);
}
import { trackPageView } from "./lib/analytics";
import { useLocation } from "react-router-dom";
import SEO from "./components/SEO";

// Placeholder component for missing pages (noindex)
const PlaceholderPage = ({ title }) => (
  <div className="container mx-auto px-4 py-8">
    <SEO title={`${title} | Trade Scan Pro`} robots="noindex,follow" />
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
      <p className="text-gray-600">This page is under development.</p>
    </div>
  </div>
);

const OfflineBanner = () => {
  const { isBackendUp } = useBackendStatus();
  if (isBackendUp) return null;
  return (
    <div className="w-full bg-red-600 text-white text-center text-sm py-2">
      Backend temporarily unavailable. Some actions are disabled.
    </div>
  );
};

function App() {
  useEffect(() => {
    // initial load
    try { trackPageView(window.location.pathname, document.title); } catch {}
  }, []);

  // Track route changes
  const PageViewTracker = () => {
    const location = useLocation();
    useEffect(() => {
      try { trackPageView(location.pathname, document.title); } catch {}
    }, [location.pathname]);
    return null;
  };
  const [cmdOpen, setCmdOpen] = React.useState(false);
  useGlobalHotkeys(setCmdOpen);
  return (
    <BackendStatusProvider>
      <AuthProvider>
        <BrowserRouter>
          {/* LatencyIndicator removed per request */}
          <SystemErrorBoundary>
            <div className="min-h-screen bg-background">
              <OfflineBanner />
              <Suspense fallback={<div className="p-8 text-center">Loading…</div>}>
              <PageViewTracker />
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
                  {/* 2FA route removed */}
                </Route>

                {/* Onboarding */}
                <Route path="/onboarding" element={
                  <ProtectedRoute>
                    <OnboardingWizard />
                  </ProtectedRoute>
                } />

                {/* Billing Routes */}
                <Route path="/checkout/success" element={<CheckoutSuccess />} />
                <Route path="/checkout/failure" element={<CheckoutFailure />} />
                <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />

                {/* Main App Routes */}
                <Route element={<EnhancedAppLayout cmdOpen={cmdOpen} setCmdOpen={setCmdOpen} />}>
                  {/* Public/Marketing Routes - Available to all users */}
                  <Route path="/" element={<Home />} />
                  <Route path="/features" element={<Features />} />
                  <Route path="/about" element={<About />} />
                  <Route path="/contact" element={<Contact />} />
                  {/* Referral short links */}
                  <Route path="/adam50" element={<ReferralApply code="ADAM50" redirectTo="/pricing" />} />
                  <Route path="/ref/:code" element={<ReferralApply redirectTo="/pricing" />} />
                  <Route path="/pricing" element={<PricingPro />} />
                  <Route path="/pricing-old" element={<Pricing />} />
                  <Route path="/stock-filter" element={<StockFilter />} />
                  <Route path="/market-scan" element={<MarketScan />} />
                  <Route path="/demo-scanner" element={<DemoScanner />} />
                  <Route path="/resources" element={<Resources />} />
                  <Route path="/press" element={<Press />} />
                  <Route path="/widgets" element={<Widgets />} />
                  <Route path="/badges" element={<Badges />} />
                  <Route path="/partners" element={<Partners />} />
                  
                  {/* Public Share Pages */}
                  <Route path="/w/:slug" element={<PlaceholderPage title="Shared Watchlist" />} />
                  <Route path="/p/:slug" element={<PlaceholderPage title="Shared Portfolio" />} />

                  {/* Marketing Pages - Using placeholders */}
                  <Route path="/product" element={<PlaceholderPage title="Product" />} />
                  <Route path="/data" element={<PlaceholderPage title="Data Coverage" />} />
                  <Route path="/use-cases" element={<PlaceholderPage title="Use Cases" />} />
                  <Route path="/changelog" element={<PlaceholderPage title="Changelog" />} />
                  <Route path="/help" element={<Help />} />
                  <Route path="/help/faq" element={<Help />} />
                  <Route path="/enterprise" element={<EnterpriseContact />} />
                  <Route path="/enterprise/contact" element={<EnterpriseContact />} />
                  <Route path="/enterprise/quote" element={<QuoteRequest />} />
                  <Route path="/enterprise/solutions" element={<SolutionsShowcase />} />

                  {/* White-label Configuration - Protected (Gold Plan) */}
                  <Route path="/enterprise/white-label" element={
                    <ProtectedRoute>
                      <WhiteLabelConfig />
                    </ProtectedRoute>
                  } />

                  {/* Protected Analytics and Referral Routes */}
                  <Route path="/app/analytics" element={
                    <ProtectedRoute>
                      <AdvancedAnalytics />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/referrals" element={
                    <ProtectedRoute>
                      <ReferralSystem />
                    </ProtectedRoute>
                  } />

                  {/* User Pages - ONLY accessible to signed-in users */}
                  <Route path="/app/dashboard" element={
                    <ProtectedRoute>
                      <AppDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/markets" element={
                    <ProtectedRoute>
                      <Markets />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/stocks" element={
                    <ProtectedRoute>
                      <Stocks />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/stocks/:symbol" element={
                    <ProtectedRoute>
                      <StockDetail />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/portfolio" element={
                    <ProtectedRoute>
                      <Portfolio />
                    </ProtectedRoute>
                  } />

                  {/* Screener Suite - Protected */}
                  <Route path="/app/screeners" element={
                    <ProtectedRoute>
                      <ScreenerLibrary />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/screeners/:id" element={
                    <ProtectedRoute>
                      <ScreenerDetail />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/screeners/new" element={
                    <ProtectedRoute>
                      <CreateScreener />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/screeners/:id/edit" element={
                    <ProtectedRoute>
                      <EditScreener />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/screeners/:id/results" element={
                    <ProtectedRoute>
                      <ScreenerResults />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/templates" element={
                    <ProtectedRoute>
                      <Templates />
                    </ProtectedRoute>
                  } />

                  {/* Market Overview - Protected */}
                  <Route path="/app/market-heatmap" element={
                    <ProtectedRoute>
                      <MarketHeatmap />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/sectors" element={
                    <ProtectedRoute>
                      <SectorsIndustries />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/top-movers" element={
                    <ProtectedRoute>
                      <TopMovers />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/pre-after-market" element={
                    <ProtectedRoute>
                      <PreAfterMarket />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/economic-calendar" element={
                    <ProtectedRoute>
                      <EconomicCalendar />
                    </ProtectedRoute>
                  } />

                  {/* News - Protected */}
                  <Route path="/app/news" element={
                    <ProtectedRoute>
                      <NewsFeed />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/news/preferences" element={
                    <ProtectedRoute>
                      <NewsPreferences />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/news/subscribe" element={
                    <ProtectedRoute>
                      <NewsSubscribe />
                    </ProtectedRoute>
                  } />

                  {/* Alerts & Signals - Protected */}
                  <Route path="/app/alerts" element={
                    <ProtectedRoute>
                      <Alerts />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/alerts/history" element={
                    <ProtectedRoute>
                      <AlertHistory />
                    </ProtectedRoute>
                  } />

                  {/* Watchlists - Protected */}
                  <Route path="/app/watchlists" element={
                    <ProtectedRoute>
                      <Watchlists />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/watchlists/:id" element={
                    <ProtectedRoute>
                      <WatchlistDetail />
                    </ProtectedRoute>
                  } />

                  {/* Developer Tools - Protected (Gold Plan) */}
                  <Route path="/app/developer" element={
                    <ProtectedRoute>
                      <DeveloperDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/developer/api-keys" element={
                    <ProtectedRoute>
                      <ApiKeyManagement />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/developer/usage-statistics" element={
                    <ProtectedRoute>
                      <UsageStatistics />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/developer/api-documentation" element={
                    <ProtectedRoute>
                      <ApiDocumentation />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/developer/console" element={
                    <ProtectedRoute>
                      <DeveloperConsole />
                    </ProtectedRoute>
                  } />

                  {/* Data Export System - Protected */}
                  <Route path="/app/exports" element={
                    <ProtectedRoute>
                      <ExportManager />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/exports/custom-report" element={
                    <ProtectedRoute>
                      <CustomReportBuilder />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/exports/scheduled" element={
                    <ProtectedRoute>
                      <ScheduledExports />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/exports/history" element={
                    <ProtectedRoute>
                      <DownloadHistory />
                    </ProtectedRoute>
                  } />

                  {/* Account Routes - Protected */}
                  <Route path="/account/profile" element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  } />
                  <Route path="/account/password" element={
                    <ProtectedRoute>
                      <ChangePassword />
                    </ProtectedRoute>
                  } />
                  <Route path="/account/notifications" element={
                    <ProtectedRoute>
                      <NotificationSettings />
                    </ProtectedRoute>
                  } />
                  <Route path="/account/billing" element={
                    <ProtectedRoute>
                      <BillingHistory />
                    </ProtectedRoute>
                  } />
                  <Route path="/account/plan" element={
                    <ProtectedRoute>
                      <CurrentPlan />
                    </ProtectedRoute>
                  } />
                  <Route path="/account/settings" element={
                    <ProtectedRoute>
                      <Settings />
                    </ProtectedRoute>
                  } />

                  {/* Admin - Protected (staff) */}
                  <Route path="/admin" element={
                    <ProtectedRoute>
                      <AdminConsole />
                    </ProtectedRoute>
                  } />

                  {/* System Routes */}
                  <Route path="/endpoint-status" element={<EndpointStatus />} />

                  {/* Docs & Content */}
                  <Route path="/docs" element={<Documentation />} />
                  <Route path="/docs/getting-started/create-account" element={<CreateAccount />} />
                  <Route path="/docs/getting-started/dashboard" element={<Dashboard />} />
                  <Route path="/docs/getting-started/first-screener" element={<FirstScreener />} />
                  <Route path="/docs/:category" element={<DocsCategory />} />
                  <Route path="/docs/:category/:slug" element={<DocArticle />} />

                  {/* Legal */}
                  <Route path="/legal/terms" element={<LegalTerms />} />
                  <Route path="/legal/privacy" element={<LegalPrivacy />} />
                </Route>

                {/* Default redirect */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
              </Suspense>
              <Toaster position="top-right" />
            </div>
          </SystemErrorBoundary>
        </BrowserRouter>
      </AuthProvider>
    </BackendStatusProvider>
  );
}

export default App;