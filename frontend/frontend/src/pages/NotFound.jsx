import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-6">
      <h1 className="text-4xl font-bold text-gray-900 mb-3">Page not found</h1>
      <p className="text-gray-600 mb-6 max-w-md">
        The page you’re looking for doesn’t exist. You can go back home or explore our pricing.
      </p>
      <div className="flex gap-3">
        <Link className="px-4 py-2 rounded-md bg-blue-600 text-white" to="/">Go Home</Link>
        <Link className="px-4 py-2 rounded-md border" to="/pricing">View Pricing</Link>
      </div>
    </div>
  );
}

