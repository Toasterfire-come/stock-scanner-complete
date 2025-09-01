import React from "react";
import { Outlet } from "react-router-dom";
import { Card, CardContent } from "../components/ui/card";

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Stock Scanner
          </h1>
          <p className="text-gray-600">
            Professional stock analysis platform
          </p>
        </div>
        <Card className="shadow-lg">
          <CardContent className="p-6">
            <Outlet />
          </CardContent>
        </Card>
        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            © 2024 Stock Scanner. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;