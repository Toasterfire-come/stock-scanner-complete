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
            <Route path="/app/dashboard" element={<Home />} />
            <Route path="/legal/terms" element={<React.Suspense fallback={null}><div /></React.Suspense>} />
            <Route path="/legal/privacy" element={<React.Suspense fallback={null}><div /></React.Suspense>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
