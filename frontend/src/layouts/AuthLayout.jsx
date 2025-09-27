import React from "react";
import { Outlet, Link } from "react-router-dom";
import { TrendingUp } from "lucide-react";
import { Card } from "../components/ui/card";

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <header className="p-4 sm:p-6">
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 sm:h-6 sm:w-6 text-white" aria-hidden="true"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
          </div>
          <span className="text-lg sm:text-xl font-bold text-gray-900">
            Trade Scan Pro
          </span>
        </Link>
      </header>
      
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full" style={{ maxWidth: 'min(90vw, clamp(24rem, 45vw, 64rem))' }}>
          <Card className="w-full p-6 sm:p-8 lg:p-10 xl:p-12 shadow-xl">
            <Outlet />
          </Card>
        </div>
      </main>
      
      <footer className="p-4 sm:p-6 text-center text-xs sm:text-sm text-gray-600">
        <p>
          © 2025 Trade Scan Pro. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default AuthLayout;