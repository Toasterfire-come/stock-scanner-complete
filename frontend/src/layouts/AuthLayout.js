import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { BarChart3 } from 'lucide-react';

const AuthLayout = () => {
  const location = useLocation();
  const isPlanSelection = location.pathname === '/auth/plan-selection';

  if (isPlanSelection) {
    // Render full-width for plan selection to avoid narrow, mobile-only layout
    return (
      <div className="min-h-screen bg-gray-50">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex justify-center items-center space-x-2 mb-8">
          <BarChart3 className="h-8 w-8 text-blue-600" />
          <span className="text-2xl font-bold text-gray-900">Trade Scan Pro</span>
        </Link>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;