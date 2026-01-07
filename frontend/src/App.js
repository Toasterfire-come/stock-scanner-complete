import React, { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/SecureAuthContext";
import { Toaster } from "sonner";
import { BackendStatusProvider, useBackendStatus } from "./context/BackendStatusContext";
import { TradingModeProvider } from "./context/TradingModeContext";
import { HelmetProvider } from "react-helmet-async";
import "./lib/quotaInterceptor"; // Global quota limit monitoring

// Components
import ProtectedRoute from "./components/ProtectedRoute";
import SkipToContent from "./components/SkipToContent";
import CookieConsent from "./components/CookieConsent";
import RouteLoadingFallback from "./components/RouteLoadingFallback";

// Layouts
import EnhancedAppLayout from "./layouts/EnhancedAppLayout.jsx";
import AuthLayout from "./layouts/AuthLayout";

import { Suspense, lazy } from "react";
// Public/marketing pages (lightweight, ok to prefetch on modern browsers)
const Home = lazy(() => import(/* webpackPrefetch: true */ "./pages/Home"));
const Features = lazy(() => import(/* webpackPrefetch: true */ "./pages/Features"));
const PricingPro = lazy(() => import(/* webpackPrefetch: true */ "./pages/PricingPro"));
const About = lazy(() => import("./pages/About"));
const Contact = lazy(() => import("./pages/Contact"));
const Pricing = lazy(() => import("./pages/Pricing"));
const StockFilter = lazy(() => import("./pages/StockFilter"));
const MarketScan = lazy(() => import("./pages/MarketScan"));
const DemoScanner = lazy(() => import("./pages/DemoScanner"));
const Resources = lazy(() => import("./pages/Resources"));
const Press = lazy(() => import("./pages/Press"));
const Widgets = lazy(() => import("./pages/Widgets"));
const Badges = lazy(() => import("./pages/Badges"));
const Partners = lazy(() => import("./pages/Partners"));
import AdvancedAnalytics from "./components/AdvancedAnalytics";
const CheckoutSuccess = lazy(() => import("./pages/billing/CheckoutSuccess"));
const CheckoutFailure = lazy(() => import("./pages/billing/CheckoutFailure"));
const Checkout = lazy(() => import("./pages/billing/Checkout"));

// PayPal Subscription Pages
const SubscriptionSuccess = lazy(() => import("./pages/SubscriptionSuccess"));
const SubscriptionCancel = lazy(() => import("./pages/SubscriptionCancel"));

// Auth pages
const SignIn = lazy(() => import("./pages/auth/SignIn.jsx"));
const SignUp = lazy(() => import("./pages/auth/SignUp.jsx"));
const PlanSelection = lazy(() => import("./pages/auth/PlanSelection"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const VerifyEmail = lazy(() => import("./pages/auth/VerifyEmail"));
const OAuthCallback = lazy(() => import("./pages/auth/OAuthCallback"));

// Onboarding
const OnboardingWizard = lazy(() => import("./pages/onboarding/OnboardingWizard"));

// App Pages (Protected)
const AppDashboard = lazy(() => import("./pages/app/AppDashboard"));
const Markets = lazy(() => import("./pages/app/Markets"));
const StockDetail = lazy(() => import("./pages/app/StockDetail"));
const EnhancedStockDetail = lazy(() => import("./pages/app/EnhancedStockDetail"));
const Stocks = lazy(() => import("./pages/app/Stocks"));
const Portfolio = lazy(() => import("./pages/app/Portfolio"));
const Watchlists = lazy(() => import("./pages/app/Watchlists"));
const Backtesting = lazy(() => import("./pages/app/Backtesting"));
const ValueHunter = lazy(() => import("./pages/app/ValueHunter"));
const IndicatorBuilder = lazy(() => import("./pages/app/IndicatorBuilder"));
const TradingJournal = lazy(() => import("./pages/app/TradingJournal"));
const TaxReporting = lazy(() => import("./pages/app/TaxReporting"));
const SharedWatchlist = lazy(() => import("./pages/app/SharedWatchlist"));
const SharedPortfolio = lazy(() => import("./pages/app/SharedPortfolio"));
const PublicProfile = lazy(() => import("./pages/app/PublicProfile"));
const PublicBacktestShare = lazy(() => import("./pages/PublicBacktestShare"));
const StrategyLeaderboard = lazy(() => import("./pages/app/StrategyLeaderboard"));
const EmbedBacktest = lazy(() => import("./pages/EmbedBacktest"));
const BlogIndex = lazy(() => import("./pages/blog/BlogIndex"));
const BlogPost = lazy(() => import("./pages/blog/BlogPost"));
const WatchlistDetail = lazy(() => import("./pages/app/WatchlistDetail"));

// Education Pages (Phase 7)
const CourseCatalog = lazy(() => import("./pages/education/CourseCatalog"));
const Glossary = lazy(() => import("./pages/education/Glossary"));
const ProgressDashboard = lazy(() => import("./pages/education/ProgressDashboard"));

// Developer Tools (Gold Plan)
const DeveloperDashboard = lazy(() => import("./pages/app/developer/DeveloperDashboard"));
const ApiKeyManagement = lazy(() => import("./pages/app/developer/ApiKeyManagement"));
const UsageStatistics = lazy(() => import("./pages/app/developer/UsageStatistics"));
const ApiDocumentation = lazy(() => import("./pages/app/developer/ApiDocumentation"));
const DeveloperConsole = lazy(() => import("./pages/app/developer/DeveloperConsole"));

// Screener Suite (Protected)
const ScreenerLibrary = lazy(() => import("./pages/app/screeners/ScreenerLibrary"));
const CreateScreener = lazy(() => import("./pages/app/screeners/CreateScreener"));
const EditScreener = lazy(() => import("./pages/app/screeners/EditScreener"));
const ScreenerResults = lazy(() => import("./pages/app/screeners/ScreenerResults"));
const ScreenerDetail = lazy(() => import("./pages/app/screeners/ScreenerDetail"));
const EnhancedCreateScreener = lazy(() => import("./pages/app/screeners/EnhancedCreateScreener"));
const EnhancedScreenerResults = lazy(() => import("./pages/app/screeners/EnhancedScreenerResults"));
const Templates = lazy(() => import("./pages/app/Templates"));

// Market Overview (Protected)
const MarketHeatmap = lazy(() => import("./pages/app/MarketHeatmap"));
const SectorsIndustries = lazy(() => import("./pages/app/SectorsIndustries"));
const TopMovers = lazy(() => import("./pages/app/TopMovers"));
const PreAfterMarket = lazy(() => import("./pages/app/PreAfterMarket"));
const EconomicCalendar = lazy(() => import("./pages/app/EconomicCalendar"));

// News & Sentiment (Re-enabled for production)
const NewsFeed = lazy(() => import("./pages/app/NewsFeed"));
const NewsPreferences = lazy(() => import("./pages/app/NewsPreferences"));
const NewsSubscribe = lazy(() => import("./pages/app/NewsSubscribe"));

// Paper Trading (MVP2 v3.4 - Basic Tier)
const PaperTrading = lazy(() => import("./pages/app/PaperTrading"));

// Options Analytics (MVP2 v3.4 - Pro Tier)
const OptionsAnalytics = lazy(() => import("./pages/app/OptionsAnalytics"));

// Alerts & Signals (Protected)
const Alerts = lazy(() => import("./pages/app/Alerts"));
const AlertHistory = lazy(() => import("./pages/app/AlertHistory"));

// Account Pages (Protected)
const Profile = lazy(() => import("./pages/account/Profile"));
const ChangePassword = lazy(() => import("./pages/account/ChangePassword"));
const NotificationSettings = lazy(() => import("./pages/account/NotificationSettings"));
const BillingHistory = lazy(() => import("./pages/account/BillingHistory"));
const CurrentPlan = lazy(() => import("./pages/account/CurrentPlan"));
const Settings = lazy(() => import("./pages/account/Settings"));

// Partner Analytics (Protected - whitelisted emails only)
import PartnerAnalyticsRoute from "./routes/PartnerAnalyticsRoute";

// System Pages
import EndpointStatus from "./pages/system/EndpointStatus";

// Content & Docs
const LegalTerms = lazy(() => import("./pages/LegalTerms"));
const LegalPrivacy = lazy(() => import("./pages/LegalPrivacy"));
const Documentation = lazy(() => import("./pages/docs/Documentation"));
const CreateAccount = lazy(() => import("./pages/docs/getting-started/CreateAccount"));
const Dashboard = lazy(() => import("./pages/docs/getting-started/Dashboard"));
const FirstScreener = lazy(() => import("./pages/docs/getting-started/FirstScreener"));
const DocsCategory = lazy(() => import("./pages/docs/DocsCategory"));
const DocArticle = lazy(() => import("./pages/docs/DocArticle"));
const EnterpriseContact = lazy(() => import("./pages/enterprise/EnterpriseContact"));
const Help = lazy(() => import("./pages/Help"));
import ReferralApply from "./pages/ReferralApply";
const AdminConsole = lazy(() => import("./pages/admin/AdminConsole"));

// Enterprise Solutions
const QuoteRequest = lazy(() => import("./pages/enterprise/QuoteRequest"));
const SolutionsShowcase = lazy(() => import("./pages/enterprise/SolutionsShowcase"));
const WhiteLabelConfig = lazy(() => import("./pages/enterprise/WhiteLabelConfig"));

// Data Export System
const ExportManager = lazy(() => import("./pages/app/exports/ExportManager"));
const CustomReportBuilder = lazy(() => import("./pages/app/exports/CustomReportBuilder"));
const ScheduledExports = lazy(() => import("./pages/app/exports/ScheduledExports"));
const DownloadHistory = lazy(() => import("./pages/app/exports/DownloadHistory"));

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
    <HelmetProvider>
    <BackendStatusProvider>
      <AuthProvider>
        <TradingModeProvider>
        <BrowserRouter>
          {/* LatencyIndicator removed per request */}
          <SkipToContent />
          <SystemErrorBoundary>
            <div id="main-content" className="min-h-screen bg-background" tabIndex="-1">
              <OfflineBanner />
              <Suspense fallback={<RouteLoadingFallback />}>
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

                {/* PayPal Subscription Routes */}
                <Route path="/subscription/success" element={<SubscriptionSuccess />} />
                <Route path="/subscription/cancel" element={<SubscriptionCancel />} />

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
                  <Route path="/blog" element={<BlogIndex />} />
                  <Route path="/blog/:slug" element={<BlogPost />} />
                  <Route path="/stock-filter" element={<StockFilter />} />
                  <Route path="/market-scan" element={<MarketScan />} />
                  <Route path="/demo-scanner" element={<DemoScanner />} />
                  <Route path="/resources" element={<Resources />} />
                  <Route path="/press" element={<Press />} />
                  <Route path="/widgets" element={<Widgets />} />
                  <Route path="/badges" element={<Badges />} />
                  <Route path="/partners" element={<Partners />} />
                  <Route path="/strategies/leaderboard" element={<StrategyLeaderboard />} />
                  
                  {/* Public Share Pages */}
                  <Route path="/w/:slug" element={<SharedWatchlist />} />
                  <Route path="/p/:slug" element={<SharedPortfolio />} />
                  <Route path="/u/:username" element={<PublicProfile />} />
                  <Route path="/share/backtest/:backtest_id" element={<PublicBacktestShare />} />
                  <Route path="/backtest/:shareSlug" element={<PublicBacktestShare />} />
                  <Route path="/embed/backtest/:slug" element={<EmbedBacktest />} />

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
                  {/* ReferralSystem component removed - not implemented yet */}
                  {/* <Route path="/app/referrals" element={
                    <ProtectedRoute>
                      <ReferralSystem />
                    </ProtectedRoute>
                  } /> */}

                  {/* Partner Analytics - Protected (whitelisted emails only) */}
                  <Route path="/partner/analytics" element={<PartnerAnalyticsRoute />} />

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
                      <EnhancedStockDetail />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/stocks/:symbol/classic" element={
                    <ProtectedRoute>
                      <StockDetail />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/portfolio" element={
                    <ProtectedRoute>
                      <Portfolio />
                    </ProtectedRoute>
                  } />

                  {/* AI Backtesting - Protected (Premium) */}
                  <Route path="/app/backtesting" element={
                    <ProtectedRoute>
                      <Backtesting />
                    </ProtectedRoute>
                  } />

                  {/* Value Hunter Portfolio - Protected (Premium) */}
                  <Route path="/app/value-hunter" element={
                    <ProtectedRoute>
                      <ValueHunter />
                    </ProtectedRoute>
                  } />

                  {/* Custom Indicator Builder - Protected (Phase 9) */}
                  <Route path="/app/indicators" element={
                    <ProtectedRoute>
                      <IndicatorBuilder />
                    </ProtectedRoute>
                  } />

                  {/* Trading Journal - Protected (Phase 9) */}
                  <Route path="/app/journal" element={
                    <ProtectedRoute>
                      <TradingJournal />
                    </ProtectedRoute>
                  } />

                  {/* Tax Reporting - Protected (Phase 9) */}
                  <Route path="/app/tax-reporting" element={
                    <ProtectedRoute>
                      <TaxReporting />
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
                      <EnhancedCreateScreener />
                    </ProtectedRoute>
                  } />
                  <Route path="/app/screeners/results" element={
                    <ProtectedRoute>
                      <EnhancedScreenerResults />
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

                  {/* News & Sentiment (Re-enabled for production) */}
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

                  {/* Paper Trading - MVP2 v3.4 (Basic Tier) */}
                  <Route path="/app/paper-trading" element={
                    <ProtectedRoute>
                      <PaperTrading />
                    </ProtectedRoute>
                  } />

                  {/* Options Analytics - MVP2 v3.4 (Pro Tier) */}
                  <Route path="/app/options" element={
                    <ProtectedRoute>
                      <OptionsAnalytics />
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
              <CookieConsent />
            </div>
          </SystemErrorBoundary>
        </BrowserRouter>
        </TradingModeProvider>
      </AuthProvider>
    </BackendStatusProvider>
    </HelmetProvider>
  );
}

export default App;