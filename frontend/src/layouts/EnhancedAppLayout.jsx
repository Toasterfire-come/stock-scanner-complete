import React, { useMemo, useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/SecureAuthContext";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { SmartBreadcrumb } from "../components/ui/breadcrumb";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "../components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "../components/ui/sheet";
import {
  BarChart3,
  TrendingUp,
  Search,
  Bell,
  User,
  Menu,
  Home,
  Activity,
  Eye,
  Target,
  AlertCircle,
  Settings,
  LogOut,
  Crown,
  FileText,
  Phone,
  HelpCircle,
  Building,
  Zap,
  ChevronDown
} from "lucide-react";
import MarketStatus from "../components/MarketStatus";
import QuickActions from "../components/QuickActions";
import LiveChat from "../components/LiveChat";

const EnhancedAppLayout = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Enhanced navigation structure with better grouping
  const navigationGroups = {
    user: {
      label: "User Pages",
      requiresAuth: true,
      items: [
        { name: "Dashboard", href: "/app/dashboard", icon: BarChart3, description: "Overview & insights" },
        { name: "Stocks", href: "/app/stocks", icon: Activity, description: "Stock analysis" },
        { name: "Markets", href: "/app/markets", icon: TrendingUp, description: "Market overview" },
        { name: "Screeners", href: "/app/screeners", icon: Search, description: "Find trading opportunities" },
        { name: "Watchlists", href: "/app/watchlists", icon: Eye, description: "Monitor favorites" },
        { name: "Portfolio", href: "/app/portfolio", icon: Target, description: "Track performance" },
        { name: "Alerts", href: "/app/alerts", icon: AlertCircle, description: "Price & volume alerts" },
        { name: "News", href: "/app/news", icon: Activity, description: "Latest market news" },
        { name: "Exports", href: "/app/exports", icon: FileText, description: "Data exports" },
        { name: "Developer", href: "/app/developer", icon: Zap, description: "API & developer tools" },
        { name: "Account", href: "/account/profile", icon: User, description: "Profile & settings" },
      ]
    },
    resources: {
      label: "Resources",
      items: [
        { name: "Features", href: "/features", icon: Activity, description: "Powerful trading tools" },
        { name: "Pricing", href: "/pricing", icon: Crown, description: "Plans for every trader" },
        { name: "Documentation", href: "/docs", icon: FileText, description: "Learn the platform" },
        { name: "Help Center", href: "/help", icon: HelpCircle, description: "Get support" },
        { name: "Enterprise", href: "/enterprise", icon: Building, description: "Solutions for institutions" },
        { name: "About", href: "/about", icon: Building, description: "Our story" },
        { name: "Contact", href: "/contact", icon: Phone, description: "Get in touch" }
      ]
    }
  };

  const isUserPage = location.pathname.startsWith("/app");
  const isOnPublicPage = !isUserPage;
  const isHome = isOnPublicPage && (location.pathname === "/" || location.pathname === "/home");
  const bottomNavVisible = isUserPage;
  const showBreadcrumbs = isUserPage || location.pathname.startsWith("/docs");

  return (
    <div className="min-h-screen bg-background">
      <LiveChat />
      {/* Enhanced Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-all duration-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo with enhanced hover effect */}
            <Link 
              to={isAuthenticated ? "/app/dashboard" : "/"} 
              className="flex items-center space-x-2 flex-shrink-0 group transition-all duration-200 hover:scale-105"
            >
              <div className="relative">
                <BarChart3 className="h-8 w-8 text-blue-600 transition-colors duration-200 group-hover:text-blue-700" />
                <div className="absolute inset-0 bg-blue-600 rounded opacity-0 group-hover:opacity-20 transition-opacity duration-200" />
              </div>
              <span className="text-xl font-bold text-gray-900 hidden sm:block">
                Trade Scan Pro
              </span>
              <span className="text-lg font-bold text-gray-900 sm:hidden">
                TSP
              </span>
            </Link>

            {/* Remove desktop dropdowns; rely on hamburger menu only */}

            {/* Removed header quick-action buttons to rely on the hamburger menu */}

            {/* Right side */}
            <div className="flex items-center space-x-3">
              {/* Market Status (hide on public pages to reduce header clutter) */}
              {!isOnPublicPage && (
                <div className="hidden lg:block">
                  <MarketStatus />
                </div>
              )}

              {isAuthenticated && user ? (
                <>
                  {/* User Plan Badge */}
                  <Badge variant="secondary" className="hidden sm:inline-flex text-xs">
                    {((user.plan || 'free').charAt(0).toUpperCase() + (user.plan || 'free').slice(1))} Plan
                  </Badge>

                  {/* User Menu */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                        <User className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56 vertical-menu max-h-[70vh] overflow-y-auto" align="end" forceMount>
                      <DropdownMenuLabel className="font-normal">
                        <div className="flex flex-col space-y-1">
                          <p className="text-sm font-medium leading-none">{user.name || user.username}</p>
                          <p className="text-xs leading-none text-muted-foreground">
                            {user.email}
                          </p>
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link to="/account/profile">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Settings</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link to="/account/plan">
                          <Crown className="mr-2 h-4 w-4" />
                          <span>Plan & Billing</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={logout}>
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Log out</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </>
              ) : (
                // Enhanced Auth buttons
                <div className="flex items-center space-x-3">
                  <Button variant="ghost" asChild className="hidden sm:inline-flex">
                    <Link to="/auth/sign-in">Sign In</Link>
                  </Button>
                  <Button asChild size="sm" className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
                    <Link to="/auth/sign-up">
                      <Zap className="h-4 w-4 mr-1" />
                      Try Free
                    </Link>
                  </Button>
                </div>
              )}

              {/* Enhanced Mobile menu */}
              <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" className={`h-9 w-9 p-0 ${isOnPublicPage ? 'md:hidden' : ''}`}>
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[300px] sm:w-[350px]">
                  <SheetHeader>
                    <SheetTitle className="text-left">Menu</SheetTitle>
                  </SheetHeader>
                  
                  <div className="mt-6 space-y-6">
                    {/* Market Status in mobile */}
                    <div className="lg:hidden">
                      <MarketStatus />
                    </div>
                    
                    {/* Mobile Navigation */}
                    <nav className="space-y-6">
                      {Object.entries(navigationGroups).map(([key, group]) => {
                        if (group.requiresAuth && !isAuthenticated) return null;
                        // On public pages, limit Resources menu to key links
                        const filteredItems = isOnPublicPage && key === 'resources'
                          ? group.items.filter((item) => ['Features', 'Pricing', 'Documentation', 'Help Center', 'Enterprise', 'About', 'Contact'].includes(item.name))
                          : group.items;
                        if (filteredItems.length === 0) return null;
                        return (
                          <div key={key}>
                            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                              {group.label}
                            </h3>
                            <div className="space-y-1">
                              {filteredItems.map((item) => {
                                const Icon = item.icon;
                                return (
                                  <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-colors ${
                                      location.pathname === item.href
                                        ? "bg-blue-100 text-blue-600"
                                        : "text-gray-700 hover:bg-gray-100"
                                    }`}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                  >
                                    <Icon className="h-5 w-5" />
                                    <div>
                                      <div>{item.name}</div>
                                      <div className="text-xs text-gray-500">{item.description}</div>
                                    </div>
                                  </Link>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Mobile Auth buttons */}
                      {!isAuthenticated && (
                        <div className="border-t pt-6 space-y-3">
                          <Link
                            to="/auth/sign-in"
                            className="flex items-center justify-center px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            Sign In
                          </Link>
                          <Link
                            to="/auth/sign-up"
                            className="flex items-center justify-center px-4 py-3 rounded-lg text-base font-medium bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 transition-colors"
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            <Zap className="h-4 w-4 mr-2" />
                            Try Free
                          </Link>
                        </div>
                      )}
                    </nav>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>

          {/* Breadcrumbs */}
          {showBreadcrumbs && (
            <div className="py-3 border-t border-gray-100">
              <SmartBreadcrumb />
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="relative">
        <Outlet />
      </main>

      {/* Quick Actions Floating Button */}
      <QuickActions />

      {/* Enhanced Footer */}
      <footer className="border-t bg-gray-50/80 backdrop-blur">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <span className="text-xl font-bold">Trade Scan Pro</span>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed">
                Professional stock screening and market intelligence platform for serious traders.
              </p>
              <div className="mt-4">
                <Badge variant="outline" className="text-xs">
                  Trusted by 50,000+ traders
                </Badge>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="/features" className="hover:text-blue-600 transition-colors">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-blue-600 transition-colors">Pricing</Link></li>
                <li><Link to="/docs" className="hover:text-blue-600 transition-colors">Documentation</Link></li>
                {isAuthenticated && (
                  <li><Link to="/app/dashboard" className="hover:text-blue-600 transition-colors">Dashboard</Link></li>
                )}
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="/about" className="hover:text-blue-600 transition-colors">About</Link></li>
                <li><Link to="/contact" className="hover:text-blue-600 transition-colors">Contact</Link></li>
                <li><Link to="/enterprise" className="hover:text-blue-600 transition-colors">Enterprise</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="/help" className="hover:text-blue-600 transition-colors">Help Center</Link></li>
                <li><Link to="/legal/privacy" className="hover:text-blue-600 transition-colors">Privacy Policy</Link></li>
                <li><Link to="/legal/terms" className="hover:text-blue-600 transition-colors">Terms of Service</Link></li>
                <li><Link to="/status" className="hover:text-blue-600 transition-colors">Status & Uptime</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t mt-8 pt-8 text-center text-sm text-gray-600">
            <p className="mb-3">&copy; 2025 Trade Scan Pro. All rights reserved. Built for serious traders.</p>
            <p>
              <a href="https://x.com/TradeScanPro" rel="me noopener" target="_blank" className="hover:text-blue-600" aria-label="Trade Scan Pro on X (Twitter)">X</a>
              <span className="mx-2">•</span>
              <a href="https://www.linkedin.com/company/tradescanpro/" rel="me noopener" target="_blank" className="hover:text-blue-600" aria-label="Trade Scan Pro on LinkedIn">LinkedIn</a>
            </p>
          </div>
        </div>
      </footer>

      {/* Mobile Bottom Navigation */}
      {bottomNavVisible && (
        <nav aria-label="Primary" className="fixed bottom-0 inset-x-0 z-50 border-t bg-white/95 dark:bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-white/75 dark:supports-[backdrop-filter]:bg-gray-900/75 md:hidden">
          <div className="grid grid-cols-5 text-xs">
            <Link to="/app/dashboard" className={`flex flex-col items-center py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${location.pathname.startsWith('/app/dashboard') ? 'text-blue-600' : 'text-gray-600 dark:text-gray-300'}`} aria-label="Dashboard" aria-current={location.pathname.startsWith('/app/dashboard') ? 'page' : undefined}>
              <BarChart3 className="h-5 w-5" />
              <span>Dashboard</span>
            </Link>
            <Link to="/app/markets" className={`flex flex-col items-center py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${location.pathname.startsWith('/app/markets') ? 'text-blue-600' : 'text-gray-600 dark:text-gray-300'}`} aria-label="Markets" aria-current={location.pathname.startsWith('/app/markets') ? 'page' : undefined}>
              <TrendingUp className="h-5 w-5" />
              <span>Markets</span>
            </Link>
            <Link to="/app/screeners" className={`flex flex-col items-center py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${location.pathname.startsWith('/app/screeners') ? 'text-blue-600' : 'text-gray-600 dark:text-gray-300'}`} aria-label="Screeners" aria-current={location.pathname.startsWith('/app/screeners') ? 'page' : undefined}>
              <Search className="h-5 w-5" />
              <span>Screeners</span>
            </Link>
            <Link to="/app/watchlists" className={`flex flex-col items-center py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${location.pathname.startsWith('/app/watchlists') ? 'text-blue-600' : 'text-gray-600 dark:text-gray-300'}`} aria-label="Watchlists" aria-current={location.pathname.startsWith('/app/watchlists') ? 'page' : undefined}>
              <Eye className="h-5 w-5" />
              <span>Watchlists</span>
            </Link>
            <Link to="/app/portfolio" className={`flex flex-col items-center py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${location.pathname.startsWith('/app/portfolio') ? 'text-blue-600' : 'text-gray-600 dark:text-gray-300'}`} aria-label="Portfolio" aria-current={location.pathname.startsWith('/app/portfolio') ? 'page' : undefined}>
              <Target className="h-5 w-5" />
              <span>Portfolio</span>
            </Link>
          </div>
          <div className="h-[env(safe-area-inset-bottom)]" />
        </nav>
      )}
    </div>
  );
};

export default EnhancedAppLayout;