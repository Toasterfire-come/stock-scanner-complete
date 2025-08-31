import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Marketing pages
import Home from "./pages/Marketing/Home";
import Features from "./pages/Marketing/Features";
import Pricing from "./pages/Marketing/Pricing";
import GenericPage from "./pages/Marketing/GenericPage";
import Status from "./pages/Marketing/Status";
import Docs from "./pages/Marketing/Docs";
import Contact from "./pages/Marketing/Contact";

// App pages
import AlertsPage from "./pages/App/Alerts";
import Portfolio from "./pages/App/Portfolio";
import Watchlists from "./pages/App/Watchlists";
import Screeners from "./pages/App/Screeners";
import Notifications from "./pages/App/Notifications";
import DesignSystem from "./pages/DesignSystem";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Public/Marketing */}
          <Route path="/" element={<Home />} />
          <Route path="/features" element={<Features />} />
          <Route path="/product" element={<GenericPage title="Product" subtitle="Overview of the platform." />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/data" element={<GenericPage title="Data Coverage" subtitle="Exchanges, asset classes and refresh rates." />} />
          <Route path="/use-cases" element={<GenericPage title="Use cases" />} />
          <Route path="/changelog" element={<GenericPage title="Changelog" />} />
          <Route path="/status" element={<Status />} />
          <Route path="/blog" element={<GenericPage title="Blog" />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/guides" element={<GenericPage title="Guides" />} />
          <Route path="/tutorials" element={<GenericPage title="Tutorials" />} />
          <Route path="/glossary" element={<GenericPage title="Glossary" />} />
          <Route path="/about" element={<GenericPage title="About" />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/careers" element={<GenericPage title="Careers" />} />
          <Route path="/legal/terms" element={<GenericPage title="Terms of Service" />} />
          <Route path="/legal/privacy" element={<GenericPage title="Privacy Policy" />} />
          <Route path="/legal/cookies" element={<GenericPage title="Cookie Policy" />} />
          <Route path="/legal/security" element={<GenericPage title="Security" />} />

          {/* Auth routes (placeholders) */}
          <Route path="/auth/sign-in" element={<GenericPage title="Sign in" />} />
          <Route path="/auth/sign-up" element={<GenericPage title="Sign up" />} />
          <Route path="/auth/callback" element={<GenericPage title="OAuth Callback" />} />
          <Route path="/auth/2fa" element={<GenericPage title="Two-factor" />} />
          <Route path="/auth/forgot-password" element={<GenericPage title="Forgot password" />} />
          <Route path="/auth/reset-password" element={<GenericPage title="Reset password" />} />
          <Route path="/auth/verify-email" element={<GenericPage title="Verify email" />} />
          <Route path="/onboarding" element={<GenericPage title="Onboarding" />} />

          {/* App Shell minimal */}
          <Route path="/app/dashboard" element={<GenericPage title="Dashboard" />} />
          <Route path="/app/notifications" element={<Notifications />} />
          <Route path="/app/search" element={<GenericPage title="Search" />} />
          <Route path="/app/command" element={<GenericPage title="Command Palette" />} />

          {/* Core in-app pages themed */}
          <Route path="/app/screeners" element={<Screeners />} />
          <Route path="/app/watchlists" element={<Watchlists />} />
          <Route path="/app/portfolio" element={<Portfolio />} />

          {/* Utilities */}
          <Route path="/design-system" element={<DesignSystem />} />

          {/* Alerts & Signals */}
          <Route path="/app/alerts" element={<AlertsPage />} />
          <Route path="/app/alerts/new" element={<AlertsPage />} />
          <Route path="/app/alerts/history" element={<GenericPage title="Alert history" />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;