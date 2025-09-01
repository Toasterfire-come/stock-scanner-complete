import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
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
            <Route path="/legal/terms" element={<LegalTerms />} />
            <Route path="/legal/privacy" element={<LegalPrivacy />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
