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
            <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
          </div>
          <span className="text-lg sm:text-xl font-bold text-gray-900">
            Trade Scan Pro
          </span>
        </Link>
      </header>
      
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md sm:max-w-lg md:max-w-xl lg:max-w-2xl xl:max-w-3xl">
          <Card className="w-full p-6 sm:p-8 md:p-10 lg:p-12 shadow-xl">
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