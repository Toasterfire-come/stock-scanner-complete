import React, { useState, useEffect } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import EnhancedButton from "../components/ui/enhanced-button";
import {
  Home,
  BarChart3,
  Search,
  Bell,
  User,
  Settings,
  Menu,
  X,
  TrendingUp,
  DollarSign,
  Shield,
  HelpCircle,
  LogOut,
  ChevronDown,
  Activity,
  FileText,
  BookOpen,
  Info,
  MessageCircle,
  CreditCard
} from "lucide-react";

const AppLayout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setUserMenuOpen(false);
  }, [location.pathname]);

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Markets', href: '/app/markets', icon: TrendingUp },
    { name: 'Stocks', href: '/app/stocks', icon: BarChart3 },
    { name: 'Portfolio', href: '/app/portfolio', icon: DollarSign },
    { name: 'Watchlists', href: '/app/watchlists', icon: Activity },
    { name: 'Screeners', href: '/app/screeners', icon: Search },
    { name: 'Alerts', href: '/app/alerts', icon: Bell },
  ];

  const userNavigation = [
    { name: 'Dashboard', href: '/app/dashboard', icon: BarChart3 },
    { name: 'Profile', href: '/account/profile', icon: User },
    { name: 'Settings', href: '/account/notifications', icon: Settings },
    { name: 'Billing', href: '/account/billing', icon: CreditCard },
    { name: 'Documentation', href: '/docs', icon: BookOpen },
    { name: 'About', href: '/about', icon: Info },
    { name: 'Features', href: '/features', icon: FileText },
    { name: 'Contact', href: '/contact', icon: MessageCircle },
    { name: 'Help Center', href: '/help', icon: HelpCircle },
  ];

  const isActiveRoute = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const docsAnchorByRoute = (pathname) => {
    if (pathname.startsWith('/app/markets')) return '/docs#stock-data';
    if (pathname.startsWith('/app/stocks')) return '/docs#stock-data';
    if (pathname.startsWith('/app/screeners')) return '/docs#screening';
    if (pathname.startsWith('/app/portfolio')) return '/docs#portfolio';
    if (pathname.startsWith('/app/watchlists')) return '/docs#watchlists';
    if (pathname.startsWith('/app/alerts')) return '/docs#alerts';
    if (pathname.startsWith('/account')) return '/docs#account-setup';
    return '/docs';
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Enhanced Navigation Header */}
      <header 
        className={`
          fixed top-0 left-0 right-0 z-50 transition-all duration-300
          ${isScrolled 
            ? 'bg-white/95 backdrop-blur-xl border-b border-gray-200/50 shadow-lg' 
            : 'bg-white/90 backdrop-blur-sm border-b border-gray-200/30'
          }
        `}
      >
        <div className="container-enhanced">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-4">
              <Link 
                to="/" 
                className="flex items-center space-x-3 hover:scale-105 transition-transform"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                    Trade Scan Pro
                  </h1>
                  <p className="text-xs text-gray-600 font-medium">
                    Professional Trading Platform
                  </p>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium
                      transition-all duration-200 hover:scale-105
                      ${isActiveRoute(item.href)
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Desktop Actions */}
            <div className="hidden lg:flex items-center space-x-4">
              {/* Live Market Status */}
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-green-50 text-green-700 text-sm font-medium border border-green-200">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>Markets Open</span>
              </div>

              {/* Notifications */}
              <EnhancedButton variant="ghost" size="sm" className="text-gray-600 hover:text-gray-900">
                <Bell className="w-5 h-5" />
              </EnhancedButton>

              {/* Contextual Docs */}
              <Link to={docsAnchorByRoute(location.pathname)} className="text-sm text-blue-700 hover:text-blue-900 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200">
                Docs
              </Link>

              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 p-2 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <ChevronDown className={`w-4 h-4 text-gray-600 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* User Dropdown with Scroll */}
                {userMenuOpen && (
                  <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-2xl border border-gray-200 shadow-2xl overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
                          <User className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">Professional Trader</p>
                          <p className="text-sm text-gray-600">Active Plan</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-2 max-h-80 overflow-y-auto">
                      {userNavigation.map((item) => {
                        const Icon = item.icon;
                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                            className="flex items-center space-x-3 w-full px-3 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                          >
                            <Icon className="w-4 h-4" />
                            <span>{item.name}</span>
                          </Link>
                        );
                      })}
                      <hr className="my-2 border-gray-200" />
                      <button className="flex items-center space-x-3 w-full px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors">
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* CTA Button */}
              <EnhancedButton variant="primary" size="sm" className="ml-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
                <Shield className="w-4 h-4" />
                Upgrade Plan
              </EnhancedButton>
            </div>

            {/* Mobile Menu Button */}
            <div className="lg:hidden flex items-center space-x-2">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="p-2 rounded-xl hover:bg-gray-50 transition-colors"
              >
                {isMobileMenuOpen ? (
                  <X className="w-6 h-6 text-gray-600" />
                ) : (
                  <Menu className="w-6 h-6 text-gray-600" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 bg-white/95 backdrop-blur-xl">
            <div className="container-enhanced py-4">
              {/* Mobile User Info */}
              <div className="flex items-center space-x-3 mb-6 p-4 rounded-2xl bg-gray-50">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Professional Trader</p>
                  <p className="text-sm text-gray-600">Active Plan</p>
                </div>
              </div>

              {/* Mobile Navigation Links */}
              <nav className="space-y-2 mb-6">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`
                        flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-base font-medium
                        transition-all duration-200
                        ${isActiveRoute(item.href)
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                        }
                      `}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Mobile Actions */}
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {userNavigation.slice(4).map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className="flex items-center space-x-3 w-full px-4 py-2 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
                <EnhancedButton variant="primary" className="w-full bg-gradient-to-r from-blue-600 to-blue-700">
                  <Shield className="w-4 h-4" />
                  Upgrade Plan
                </EnhancedButton>
                <EnhancedButton variant="outline" className="w-full border-gray-300 text-gray-700">
                  <Settings className="w-4 h-4" />
                  Account Settings
                </EnhancedButton>
                <EnhancedButton variant="ghost" className="w-full text-red-600">
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </EnhancedButton>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="pt-16">
        <div className="animate-fade-in">
          <Outlet />
        </div>
      </main>

      {/* Enhanced Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 mt-20">
        <div className="container-enhanced py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">Trade Scan Pro</h3>
                  <p className="text-sm text-gray-600">Professional Trading Platform</p>
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                Empowering traders with professional-grade tools, real-time data, and advanced analytics 
                to make informed investment decisions with comprehensive documentation and support.
              </p>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>99.9% Uptime • Professional Security</span>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-semibold mb-4 text-gray-900">Platform</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="/app/stocks" className="hover:text-gray-900 transition-colors">Stock Scanner</Link></li>
                <li><Link to="/app/screeners" className="hover:text-gray-900 transition-colors">Custom Screeners</Link></li>
                <li><Link to="/app/portfolio" className="hover:text-gray-900 transition-colors">Portfolio Tracker</Link></li>
                <li><Link to="/app/alerts" className="hover:text-gray-900 transition-colors">Price Alerts</Link></li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h4 className="font-semibold mb-4 text-gray-900">Support</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="/docs" className="hover:text-gray-900 transition-colors">Documentation</Link></li>
                <li><Link to="/help" className="hover:text-gray-900 transition-colors">Help Center</Link></li>
                <li><Link to="/contact" className="hover:text-gray-900 transition-colors">Contact Us</Link></li>
                <li><Link to="/endpoint-status" className="hover:text-gray-900 transition-colors">System Status</Link></li>
              </ul>
            </div>
          </div>

          <hr className="my-8 border-gray-200" />

          <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
            <p>&copy; 2024 Trade Scan Pro. All rights reserved.</p>
            <div className="flex items-center space-x-4 mt-4 sm:mt-0">
              <Link to="/legal/privacy" className="hover:text-gray-900 transition-colors">Privacy</Link>
              <Link to="/legal/terms" className="hover:text-gray-900 transition-colors">Terms</Link>
              {/* watermark removed */}
            </div>
          </div>
        </div>
      </footer>

      {/* Click outside handler for user menu */}
      {userMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setUserMenuOpen(false)}
        />
      )}
    </div>
  );
};

export default AppLayout;