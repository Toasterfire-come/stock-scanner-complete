import React, { Suspense } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "sonner";
import { BackendStatusProvider, useBackendStatus } from "./context/BackendStatusContext";
import { Skeleton } from "./components/ui/skeleton";

// Layouts
import AppLayout from "./layouts/AppLayout.js";
import AuthLayout from "./layouts/AuthLayout";

// Auth Pages (lazy)
const SignIn = React.lazy(() => import("./pages/auth/SignIn"));
const SignUp = React.lazy(() => import("./pages/auth/SignUp"));
const ForgotPassword = React.lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = React.lazy(() => import("./pages/auth/ResetPassword"));
const VerifyEmail = React.lazy(() => import("./pages/auth/VerifyEmail"));
const OAuthCallback = React.lazy(() => import("./pages/auth/OAuthCallback"));
const TwoFactorAuth = React.lazy(() => import("./pages/auth/TwoFactorAuth"));

// Onboarding (lazy)
const OnboardingWizard = React.lazy(() => import("./pages/onboarding/OnboardingWizard"));

// Public Pages (lazy)
const Home = React.lazy(() => import("./pages/Home"));
const Features = React.lazy(() => import("./pages/Features"));
const About = React.lazy(() => import("./pages/About"));
const Contact = React.lazy(() => import("./pages/Contact"));
const PricingPro = React.lazy(() => import("./pages/PricingPro"));
const Pricing = React.lazy(() => import("./pages/Pricing"));
const AdvancedAnalytics = React.lazy(() => import("./components/AdvancedAnalytics"));
const ReferralSystem = React.lazy(() => import("./components/ReferralSystem"));
const CheckoutSuccess = React.lazy(() => import("./pages/billing/CheckoutSuccess"));
const CheckoutFailure = React.lazy(() => import("./pages/billing/CheckoutFailure"));

// App Pages (lazy)
const AppDashboard = React.lazy(() => import("./pages/app/AppDashboard"));
const Markets = React.lazy(() => import("./pages/app/Markets"));
const StockDetail = React.lazy(() => import("./pages/app/StockDetail"));
const Stocks = React.lazy(() => import("./pages/app/Stocks"));
const Portfolio = React.lazy(() => import("./pages/app/Portfolio"));
const Watchlists = React.lazy(() => import("./pages/app/Watchlists"));
const WatchlistDetail = React.lazy(() => import("./pages/app/WatchlistDetail"));

// Screener Suite (lazy)
const ScreenerLibrary = React.lazy(() => import("./pages/app/screeners/ScreenerLibrary"));
const CreateScreener = React.lazy(() => import("./pages/app/screeners/CreateScreener"));
const EditScreener = React.lazy(() => import("./pages/app/screeners/EditScreener"));
const ScreenerResults = React.lazy(() => import("./pages/app/screeners/ScreenerResults"));
const Templates = React.lazy(() => import("./pages/app/Templates"));

// Market Overview (lazy)
const MarketHeatmap = React.lazy(() => import("./pages/app/MarketHeatmap"));
const SectorsIndustries = React.lazy(() => import("./pages/app/SectorsIndustries"));
const TopMovers = React.lazy(() => import("./pages/app/TopMovers"));
const PreAfterMarket = React.lazy(() => import("./pages/app/PreAfterMarket"));
const EconomicCalendar = React.lazy(() => import("./pages/app/EconomicCalendar"));

// News (lazy)
const NewsFeed = React.lazy(() => import("./pages/app/NewsFeed"));
const NewsPreferences = React.lazy(() => import("./pages/app/NewsPreferences"));
const NewsSubscribe = React.lazy(() => import("./pages/app/NewsSubscribe"));

// Alerts & Signals (lazy)
const Alerts = React.lazy(() => import("./pages/app/Alerts"));
const AlertHistory = React.lazy(() => import("./pages/app/AlertHistory"));

// Account Pages (lazy)
const Profile = React.lazy(() => import("./pages/account/Profile"));
const ChangePassword = React.lazy(() => import("./pages/account/ChangePassword"));
const NotificationSettings = React.lazy(() => import("./pages/account/NotificationSettings"));
const BillingHistory = React.lazy(() => import("./pages/account/BillingHistory"));
const CurrentPlan = React.lazy(() => import("./pages/account/CurrentPlan"));

// System Pages (lazy)
const EndpointStatus = React.lazy(() => import("./pages/system/EndpointStatus"));

// Content & Docs (lazy)
const LegalTerms = React.lazy(() => import("./pages/LegalTerms"));
const LegalPrivacy = React.lazy(() => import("./pages/LegalPrivacy"));
const Documentation = React.lazy(() => import("./pages/docs/DocumentationSimple"));
const EnterpriseContact = React.lazy(() => import("./pages/EnterpriseContact"));

// Mobile routes removed as requested

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
  return (
    <BackendStatusProvider>
      <AuthProvider>
        <BrowserRouter>
          <LatencyIndicator />
          <SystemErrorBoundary>
            <div className="min-h-screen bg-background">
              <OfflineBanner />
              <Suspense fallback={<div className="container mx-auto px-4 py-8"><div className="space-y-4"><Skeleton className="h-8 w-1/3" /><Skeleton className="h-64 w-full" /><Skeleton className="h-96 w-full" /></div></div>}>
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
                  <Route path="/enterprise" element={<EnterpriseContact />} />

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