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

// Public Pages
import Home from "./pages/Home";
import Features from "./pages/Features";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Pricing from "./pages/Pricing";

// App Pages
import AppDashboard from "./pages/app/AppDashboard";
import Markets from "./pages/app/Markets";
import StockDetail from "./pages/app/StockDetail";
import Stocks from "./pages/app/Stocks";
import Portfolio from "./pages/app/Portfolio";
import Watchlists from "./pages/app/Watchlists";
import Screeners from "./pages/app/Screeners";
import Alerts from "./pages/app/Alerts";
import NewsFeed from "./pages/app/NewsFeed";

// Account Pages
import Profile from "./pages/account/Profile";

// Error Boundary
import SystemErrorBoundary from "./components/SystemErrorBoundary";

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
        <SystemErrorBoundary>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Auth Routes */}
              <Route element={<AuthLayout />}>
                <Route path="/auth/sign-in" element={<SignIn />} />
                <Route path="/auth/sign-up" element={<SignUp />} />
                <Route path="/auth/forgot-password" element={<ForgotPassword />} />
              </Route>

              {/* Main App Routes */}
              <Route element={<AppLayout />}>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/features" element={<Features />} />
                <Route path="/about" element={<About />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/pricing" element={<Pricing />} />

                {/* App Routes */}
                <Route path="/app/dashboard" element={<AppDashboard />} />
                <Route path="/app/markets" element={<Markets />} />
                <Route path="/app/stocks" element={<Stocks />} />
                <Route path="/app/stocks/:symbol" element={<StockDetail />} />
                <Route path="/app/portfolio" element={<Portfolio />} />
                <Route path="/app/screeners" element={<Screeners />} />
                <Route path="/app/watchlists" element={<Watchlists />} />
                <Route path="/app/alerts" element={<Alerts />} />
                <Route path="/app/news" element={<NewsFeed />} />

                {/* Account Routes */}
                <Route path="/account/profile" element={<Profile />} />
              </Route>

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