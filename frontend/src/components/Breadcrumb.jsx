import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const Breadcrumb = ({ customItems = null }) => {
  const location = useLocation();

  const pathSegments = location.pathname.split('/').filter(Boolean);

  // Custom breadcrumb mapping for better labels
  const labelMap = {
    'app': 'Dashboard',
    'auth': 'Account',
    'sign-in': 'Sign In',
    'sign-up': 'Sign Up',
    'forgot-password': 'Forgot Password',
    'reset-password': 'Reset Password',
    'screener': 'Stock Screener',
    'scanner': 'Market Scanner',
    'portfolio': 'Portfolio',
    'watchlists': 'Watchlists',
    'alerts': 'Alerts',
    'account': 'My Account',
    'billing': 'Billing',
    'settings': 'Settings',
    'docs': 'Documentation',
    'getting-started': 'Getting Started',
    'stock-filter': 'Stock Filter',
    'market-scan': 'Market Scan',
  };

  const formatLabel = (segment) => {
    if (labelMap[segment]) return labelMap[segment];
    return segment
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Use custom items if provided, otherwise generate from path
  const items = customItems || pathSegments.map((segment, index) => ({
    label: formatLabel(segment),
    path: '/' + pathSegments.slice(0, index + 1).join('/'),
  }));

  if (items.length === 0 && !customItems) {
    return null; // Don't show breadcrumb on homepage
  }

  return (
    <nav aria-label="Breadcrumb" className="py-3 px-4 bg-gray-50 border-b">
      <ol className="flex items-center space-x-2 text-sm max-w-7xl mx-auto">
        <li>
          <Link
            to="/"
            className="text-gray-500 hover:text-gray-700 transition-colors flex items-center"
            aria-label="Home"
          >
            <Home className="h-4 w-4" />
          </Link>
        </li>

        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={item.path || index} className="flex items-center">
              <ChevronRight className="h-4 w-4 text-gray-400 mx-1" />
              {isLast ? (
                <span className="text-gray-900 font-medium" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.path}
                  className="text-gray-500 hover:text-gray-700 transition-colors"
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb;
