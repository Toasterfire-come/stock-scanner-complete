import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import { Features, Product, DataCoverage, UseCases, Changelog, Docs, Guides, Tutorials, Glossary, About, Contact, Careers, Blog, Help, FAQ, Community, Roadmap } from "./pages/Marketing";
import Home from "./pages/Home";
import Pricing from "./pages/Pricing";
import LegalTerms from "./pages/LegalTerms";
import LegalPrivacy from "./pages/LegalPrivacy";
import AppDashboard from "./pages/AppDashboard";
import Markets from "./pages/Markets";
import Alerts from "./pages/Alerts";
import Notifications from "./pages/Notifications";
import SignIn from "./pages/SignIn";
import { AuthProvider } from "./context/AuthContext";
import Stocks from "./pages/Stocks";
import StockDetail from "./pages/StockDetail";
import Watchlists from "./pages/Watchlists";
import Portfolio from "./pages/Portfolio";
import Status from "./pages/Status";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}> 
            <Route path="/" element={<Home />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/auth/sign-in" element={<SignIn />} />
            <Route path="/app/dashboard" element={<AppDashboard />} />
            <Route path="/app/markets" element={<Markets />} />
            <Route path="/app/alerts" element={<Alerts />} />
            <Route path="/app/notifications" element={<Notifications />} />
            <Route path="/app/stocks" element={<Stocks />} />
            <Route path="/app/stocks/:symbol" element={<StockDetail />} />
            <Route path="/app/watchlists" element={<Watchlists />} />
            <Route path="/app/portfolio" element={<Portfolio />} />
            <Route path="/app/screeners" element={<Screeners />} />
            <Route path="/features" element={<Features />} />
            <Route path="/product" element={<Product />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/data" element={<DataCoverage />} />
            <Route path="/use-cases" element={<UseCases />} />
            <Route path="/changelog" element={<Changelog />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/guides" element={<Guides />} />
            <Route path="/tutorials" element={<Tutorials />} />
            <Route path="/glossary" element={<Glossary />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/careers" element={<Careers />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/help" element={<Help />} />
            <Route path="/help/faq" element={<FAQ />} />
            <Route path="/community" element={<Community />} />
            <Route path="/roadmap" element={<Roadmap />} />
            <Route path="/status" element={<Status />} />
            <Route path="/legal/terms" element={<LegalTerms />} />
            <Route path="/legal/privacy" element={<LegalPrivacy />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
