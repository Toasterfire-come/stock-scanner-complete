import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Providers from './components/Providers';
import Nav from './components/Nav';
import './App.css';

// Lazy pages
const EndpointStatus = lazy(() => import('./pages/system/EndpointStatus'));
const MarketOverview = lazy(() => import('./pages/market/Overview'));
const NewsFeed = lazy(() => import('./pages/news/Feed'));
const Profile = lazy(() => import('./pages/account/Profile'));
const Login = lazy(() => import('./pages/auth/Login'));
const SignUp = lazy(() => import('./pages/auth/SignUp'));
const Onboarding = lazy(() => import('./pages/onboarding/Onboarding'));
const Pricing = lazy(() => import('./pages/billing/Pricing'));

function Shell({ children }) {
  return (
    <div className="min-h-screen">
      <Nav />
      <main className="py-6">{children}</main>
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <Providers>
        <BrowserRouter>
          <Suspense fallback={<div className="max-w-5xl mx-auto p-4"><div className="h-10 w-64 bg-muted animate-pulse rounded mb-4"/><div className="h-32 w-full bg-muted animate-pulse rounded"/></div>}>
            <Routes>
              {/* Public marketing routes */}
              <Route path="/" element={<Shell><MarketOverview /></Shell>} />
              <Route path="/billing" element={<Shell><Pricing /></Shell>} />
              <Route path="/endpoint-status" element={<Shell><EndpointStatus /></Shell>} />

              {/* Auth routes */}
              <Route path="/auth/login" element={<Shell><Login /></Shell>} />
              <Route path="/auth/sign-up" element={<Shell><SignUp /></Shell>} />
              <Route path="/onboarding" element={<Shell><Onboarding /></Shell>} />

              {/* App core routes */}
              <Route path="/app/market" element={<Shell><MarketOverview /></Shell>} />
              <Route path="/news" element={<Shell><NewsFeed /></Shell>} />
              <Route path="/account" element={<Shell><Profile /></Shell>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </Providers>
    </div>
  );
}

export default App;