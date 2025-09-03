import React, { Suspense } from "react";
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { Toaster } from "sonner";
import { BackendStatusProvider, useBackendStatus } from "./context/BackendStatusContext";
import { AuthProvider } from "./context/AuthContext";
import SystemErrorBoundary from "./components/SystemErrorBoundary";
import LatencyIndicator from "./components/LatencyIndicator";
import AppLayout from "./layouts/AppLayout";
import AuthLayout from "./layouts/AuthLayout";
import { Skeleton } from "./components/ui/skeleton";

// Lazy pages
const SignIn = React.lazy(() => import("./pages/auth/SignIn"));
const SignUp = React.lazy(() => import("./pages/auth/SignUp"));
const ForgotPassword = React.lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = React.lazy(() => import("./pages/auth/ResetPassword"));
const VerifyEmail = React.lazy(() => import("./pages/auth/VerifyEmail"));
const OAuthCallback = React.lazy(() => import("./pages/auth/OAuthCallback"));
const TwoFactorAuth = React.lazy(() => import("./pages/auth/TwoFactorAuth"));

const OnboardingWizard = React.lazy(() => import("./pages/onboarding/OnboardingWizard"));

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

const AppDashboard = React.lazy(() => import("./pages/app/AppDashboard"));
const Markets = React.lazy(() => import("./pages/app/Markets"));
const StockDetail = React.lazy(() => import("./pages/app/StockDetail"));
const Stocks = React.lazy(() => import("./pages/app/Stocks"));
const Portfolio = React.lazy(() => import("./pages/app/Portfolio"));
const Watchlists = React.lazy(() => import("./pages/app/Watchlists"));
const WatchlistDetail = React.lazy(() => import("./pages/app/WatchlistDetail"));

const ScreenerLibrary = React.lazy(() => import("./pages/app/screeners/ScreenerLibrary"));
const CreateScreener = React.lazy(() => import("./pages/app/screeners/CreateScreener"));
const EditScreener = React.lazy(() => import("./pages/app/screeners/EditScreener"));
const ScreenerResults = React.lazy(() => import("./pages/app/screeners/ScreenerResults"));
const Templates = React.lazy(() => import("./pages/app/Templates"));

const MarketHeatmap = React.lazy(() => import("./pages/app/MarketHeatmap"));
const SectorsIndustries = React.lazy(() => import("./pages/app/SectorsIndustries"));
const TopMovers = React.lazy(() => import("./pages/app/TopMovers"));
const PreAfterMarket = React.lazy(() => import("./pages/app/PreAfterMarket"));
const EconomicCalendar = React.lazy(() => import("./pages/app/EconomicCalendar"));

const NewsFeed = React.lazy(() => import("./pages/app/NewsFeed"));
const NewsPreferences = React.lazy(() => import("./pages/app/NewsPreferences"));
const NewsSubscribe = React.lazy(() => import("./pages/app/NewsSubscribe"));

const Alerts = React.lazy(() => import("./pages/app/Alerts"));
const AlertHistory = React.lazy(() => import("./pages/app/AlertHistory"));

const Profile = React.lazy(() => import("./pages/account/Profile"));
const ChangePassword = React.lazy(() => import("./pages/account/ChangePassword"));
const NotificationSettings = React.lazy(() => import("./pages/account/NotificationSettings"));
const BillingHistory = React.lazy(() => import("./pages/account/BillingHistory"));
const CurrentPlan = React.lazy(() => import("./pages/account/CurrentPlan"));

const EndpointStatus = React.lazy(() => import("./pages/system/EndpointStatus"));

const LegalTerms = React.lazy(() => import("./pages/LegalTerms"));
const LegalPrivacy = React.lazy(() => import("./pages/LegalPrivacy"));
const Documentation = React.lazy(() => import("./pages/docs/DocumentationSimple"));
const EnterpriseContact = React.lazy(() => import("./pages/EnterpriseContact"));

const Fallback = () => (
  <div className="container mx-auto px-4 py-8">
    <div className="space-y-4">
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-96 w-full" />
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

function Root() {
  return (
    <BackendStatusProvider>
      <AuthProvider>
        <LatencyIndicator />
        <SystemErrorBoundary>
          <div className="min-h-screen bg-background">
            <OfflineBanner />
            <Suspense fallback={<Fallback />}>
              <Outlet />
            </Suspense>
            <Toaster position="top-right" />
          </div>
        </SystemErrorBoundary>
      </AuthProvider>
    </BackendStatusProvider>
  );
}

const errorElement = (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-2xl font-bold">Something went wrong</h1>
    <p className="text-gray-600 mt-2">Please try again or navigate back to home.</p>
  </div>
);

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement,
    children: [
      // Auth Routes
      {
        element: <AuthLayout />,
        children: [
          { path: "auth/sign-in", element: (<Suspense fallback={<Fallback />}><SignIn /></Suspense>) },
          { path: "auth/sign-up", element: (<Suspense fallback={<Fallback />}><SignUp /></Suspense>) },
          { path: "auth/forgot-password", element: (<Suspense fallback={<Fallback />}><ForgotPassword /></Suspense>) },
          { path: "auth/reset-password", element: (<Suspense fallback={<Fallback />}><ResetPassword /></Suspense>) },
          { path: "auth/verify-email", element: (<Suspense fallback={<Fallback />}><VerifyEmail /></Suspense>) },
          { path: "auth/oauth-callback", element: (<Suspense fallback={<Fallback />}><OAuthCallback /></Suspense>) },
          { path: "auth/2fa", element: (<Suspense fallback={<Fallback />}><TwoFactorAuth /></Suspense>) },
        ],
      },

      // Onboarding
      { path: "onboarding", element: (<Suspense fallback={<Fallback />}><OnboardingWizard /></Suspense>) },

      // Main App Routes
      {
        element: <AppLayout />,
        children: [
          // Public
          { index: true, element: (<Suspense fallback={<Fallback />}><Home /></Suspense>) },
          { path: "features", element: (<Suspense fallback={<Fallback />}><Features /></Suspense>) },
          { path: "about", element: (<Suspense fallback={<Fallback />}><About /></Suspense>) },
          { path: "contact", element: (<Suspense fallback={<Fallback />}><Contact /></Suspense>) },
          { path: "pricing", element: (<Suspense fallback={<Fallback />}><PricingPro /></Suspense>) },
          { path: "pricing-old", element: (<Suspense fallback={<Fallback />}><Pricing /></Suspense>) },
          { path: "app/analytics", element: (<Suspense fallback={<Fallback />}><AdvancedAnalytics /></Suspense>) },
          { path: "app/referrals", element: (<Suspense fallback={<Fallback />}><ReferralSystem /></Suspense>) },

          // Billing
          { path: "checkout/success", element: (<Suspense fallback={<Fallback />}><CheckoutSuccess /></Suspense>) },
          { path: "checkout/failure", element: (<Suspense fallback={<Fallback />}><CheckoutFailure /></Suspense>) },

          // App
          { path: "app/dashboard", element: (<Suspense fallback={<Fallback />}><AppDashboard /></Suspense>) },
          { path: "app/markets", element: (<Suspense fallback={<Fallback />}><Markets /></Suspense>) },
          { path: "app/stocks", element: (<Suspense fallback={<Fallback />}><Stocks /></Suspense>) },
          { path: "app/stocks/:symbol", element: (<Suspense fallback={<Fallback />}><StockDetail /></Suspense>) },
          { path: "app/portfolio", element: (<Suspense fallback={<Fallback />}><Portfolio /></Suspense>) },

          // Screeners
          { path: "app/screeners", element: (<Suspense fallback={<Fallback />}><ScreenerLibrary /></Suspense>) },
          { path: "app/screeners/new", element: (<Suspense fallback={<Fallback />}><CreateScreener /></Suspense>) },
          { path: "app/screeners/:id/edit", element: (<Suspense fallback={<Fallback />}><EditScreener /></Suspense>) },
          { path: "app/screeners/:id/results", element: (<Suspense fallback={<Fallback />}><ScreenerResults /></Suspense>) },
          { path: "app/templates", element: (<Suspense fallback={<Fallback />}><Templates /></Suspense>) },

          // Market Overview
          { path: "app/market-heatmap", element: (<Suspense fallback={<Fallback />}><MarketHeatmap /></Suspense>) },
          { path: "app/sectors", element: (<Suspense fallback={<Fallback />}><SectorsIndustries /></Suspense>) },
          { path: "app/top-movers", element: (<Suspense fallback={<Fallback />}><TopMovers /></Suspense>) },
          { path: "app/pre-after-market", element: (<Suspense fallback={<Fallback />}><PreAfterMarket /></Suspense>) },
          { path: "app/economic-calendar", element: (<Suspense fallback={<Fallback />}><EconomicCalendar /></Suspense>) },

          // News
          { path: "app/news", element: (<Suspense fallback={<Fallback />}><NewsFeed /></Suspense>) },
          { path: "app/news/preferences", element: (<Suspense fallback={<Fallback />}><NewsPreferences /></Suspense>) },
          { path: "app/news/subscribe", element: (<Suspense fallback={<Fallback />}><NewsSubscribe /></Suspense>) },

          // Alerts
          { path: "app/alerts", element: (<Suspense fallback={<Fallback />}><Alerts /></Suspense>) },
          { path: "app/alerts/history", element: (<Suspense fallback={<Fallback />}><AlertHistory /></Suspense>) },

          // Watchlists
          { path: "app/watchlists", element: (<Suspense fallback={<Fallback />}><Watchlists /></Suspense>) },
          { path: "app/watchlists/:id", element: (<Suspense fallback={<Fallback />}><WatchlistDetail /></Suspense>) },

          // Account
          { path: "account/profile", element: (<Suspense fallback={<Fallback />}><Profile /></Suspense>) },
          { path: "account/password", element: (<Suspense fallback={<Fallback />}><ChangePassword /></Suspense>) },
          { path: "account/notifications", element: (<Suspense fallback={<Fallback />}><NotificationSettings /></Suspense>) },
          { path: "account/billing", element: (<Suspense fallback={<Fallback />}><BillingHistory /></Suspense>) },
          { path: "account/plan", element: (<Suspense fallback={<Fallback />}><CurrentPlan /></Suspense>) },

          // System
          { path: "endpoint-status", element: (<Suspense fallback={<Fallback />}><EndpointStatus /></Suspense>) },

          // Docs & Content
          { path: "docs", element: (<Suspense fallback={<Fallback />}><Documentation /></Suspense>) },
          { path: "enterprise", element: (<Suspense fallback={<Fallback />}><EnterpriseContact /></Suspense>) },

          // Legal
          { path: "legal/terms", element: (<Suspense fallback={<Fallback />}><LegalTerms /></Suspense>) },
          { path: "legal/privacy", element: (<Suspense fallback={<Fallback />}><LegalPrivacy /></Suspense>) },

          { path: "*", element: <Navigate to="/" replace /> },
        ],
      },
    ],
  },
]);

