import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/SecureAuthContext";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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
  Newspaper,
  Settings,
  LogOut,
  Crown,
  FileText,
  Phone,
  HelpCircle,
  Building
} from "lucide-react";
import MarketStatus from "../components/MarketStatus";
import ThemeToggle from "../components/ThemeToggle";

const AppLayout = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Marketing pages - available to all users
  const marketingNavigation = [
    { name: "Home", href: "/", icon: Home },
    { name: "Features", href: "/features", icon: Activity },
    { name: "About", href: "/about", icon: FileText },
    { name: "Contact", href: "/contact", icon: Phone },
    { name: "Pricing", href: "/pricing", icon: Crown },
    { name: "Help", href: "/help", icon: HelpCircle },
    { name: "Enterprise", href: "/enterprise", icon: Building },
  ];

  // User pages - only accessible to signed-in users
  const userNavigation = [
    { name: "Dashboard", href: "/app/dashboard", icon: BarChart3 },
    { name: "Markets", href: "/app/markets", icon: TrendingUp },
    { name: "Stocks", href: "/app/stocks", icon: Activity },
    { name: "Portfolio", href: "/app/portfolio", icon: Target },
    { name: "Watchlists", href: "/app/watchlists", icon: Eye },
    { name: "Screeners", href: "/app/screeners", icon: Search },
    { name: "Alerts", href: "/app/alerts", icon: AlertCircle },
  ];

  const isUserPage = location.pathname.startsWith("/app");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-14 sm:h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" aria-hidden="true"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
              <span className="text-lg sm:text-2xl font-bold text-gray-900 hidden sm:block">
                Trade Scan Pro
              </span>
              <span className="text-lg font-bold text-gray-900 sm:hidden">
                TSP
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                // Show both user pages and marketing pages in dropdown for authenticated users
                <div className="flex space-x-2">
                  {/* User Pages Dropdown */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="text-sm font-medium">
                        App
                        <Menu className="h-4 w-4 ml-2" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-48 vertical-menu max-h-[70vh] overflow-y-auto" align="start">
                      {userNavigation.map((item) => (
                        <DropdownMenuItem key={item.name} asChild>
                          <Link
                            to={item.href}
                            className={`flex items-center space-x-2 ${
                              location.pathname === item.href
                                ? "text-blue-600"
                                : "text-gray-600"
                            }`}
                          >
                            <item.icon className="h-4 w-4" />
                            <span>{item.name}</span>
                          </Link>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>

                  {/* Marketing Pages Dropdown */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="text-sm font-medium">
                        Pages
                        <Menu className="h-4 w-4 ml-2" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-48 vertical-menu max-h-[70vh] overflow-y-auto" align="start">
                      {marketingNavigation.map((item) => (
                        <DropdownMenuItem key={item.name} asChild>
                          <Link
                            to={item.href}
                            className={`flex items-center space-x-2 ${
                              location.pathname === item.href
                                ? "text-blue-600"
                                : "text-gray-600"
                            }`}
                          >
                            <item.icon className="h-4 w-4" />
                            <span>{item.name}</span>
                          </Link>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ) : (
                // Show only marketing pages for non-authenticated users
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="text-sm font-medium">
                      Pages
                      <Menu className="h-4 w-4 ml-2" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-48 vertical-menu max-h-[70vh] overflow-y-auto" align="start">
                    {marketingNavigation.map((item) => (
                      <DropdownMenuItem key={item.name} asChild>
                        <Link
                          to={item.href}
                          className={`flex items-center space-x-2 ${
                            location.pathname === item.href
                              ? "text-blue-600"
                              : "text-gray-600"
                          }`}
                        >
                          <item.icon className="h-4 w-4" />
                          <span>{item.name}</span>
                        </Link>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              {/* Market Status - always show */}
              <div className="hidden md:block">
                <MarketStatus />
              </div>

              {/* Theme toggle */}
              <ThemeToggle />

              {isAuthenticated && user ? (
                <>
                  {/* User badge */}
                  <Badge variant="secondary" className="hidden sm:inline-flex text-xs">
                    {user.plan || 'Free'} Plan
                  </Badge>

                  {/* User menu - only show for authenticated users */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                        <User className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56 vertical-menu max-h-[70vh] overflow-y-auto" align="end" forceMount>
                      <div className="flex items-center justify-start gap-2 p-2">
                        <div className="flex flex-col space-y-1 leading-none">
                          <p className="font-medium">{user.name || user.username}</p>
                          <p className="w-[200px] truncate text-sm text-muted-foreground">
                            {user.email}
                          </p>
                        </div>
                      </div>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link to="/account/profile">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Profile</span>
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
                // Auth buttons for non-authenticated users
                <div className="flex items-center space-x-2 sm:space-x-4">
                  <Button variant="ghost" asChild className="hidden sm:inline-flex">
                    <Link to="/auth/sign-in">Sign In</Link>
                  </Button>
                  <Button asChild size="sm" className="text-sm px-3 sm:px-4">
                    <Link to="/auth/sign-up">Try Now for Free</Link>
                  </Button>
                </div>
              )}

              {/* Mobile menu trigger */}
              <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" className="sm:hidden h-8 w-8 p-0">
                    <Menu className="h-4 w-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[280px] sm:w-[350px]">
                  <div className="mt-6">
                    {/* Market Status in mobile */}
                    <div className="mb-6 md:hidden">
                      <MarketStatus />
                    </div>
                    
                    <nav className="flex flex-col space-y-3">
                      {/* Show user pages first for authenticated users */}
                      {isAuthenticated && (
                        <>
                          <div className="text-sm font-medium text-gray-500 px-3 py-2 border-b">
                            App Pages
                          </div>
                          {userNavigation.map((item) => {
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
                                <span>{item.name}</span>
                              </Link>
                            );
                          })}
                          <div className="text-sm font-medium text-gray-500 px-3 py-2 border-b border-t mt-4">
                            Marketing Pages
                          </div>
                        </>
                      )}
                      
                      {/* Marketing pages */}
                      {marketingNavigation.map((item) => {
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
                            <span>{item.name}</span>
                          </Link>
                        );
                      })}
                      
                      {/* Mobile Auth buttons for non-authenticated users */}
                      {!isAuthenticated && (
                        <div className="border-t pt-4 mt-4 space-y-3">
                          <Link
                            to="/auth/sign-in"
                            className="flex items-center justify-center px-3 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            Sign In
                          </Link>
                          <Link
                            to="/auth/sign-up"
                            className="flex items-center justify-center px-3 py-3 rounded-lg text-base font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            Try Now for Free
                          </Link>
                        </div>
                      )}
                    </nav>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t bg-gray-50">
        <div className="container mx-auto px-4 py-8 sm:py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <span className="text-lg sm:text-xl font-bold">Trade Scan Pro</span>
              </div>
              <p className="text-gray-600 text-sm sm:text-base">
                Professional stock screening and market intelligence platform.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <Link to="/features" className="hover:text-blue-600">
                    Features
                  </Link>
                </li>
                <li>
                  <Link to="/pricing" className="hover:text-blue-600">
                    Pricing
                  </Link>
                </li>
                {isAuthenticated && (
                  <li>
                    <Link to="/app/dashboard" className="hover:text-blue-600">
                      Dashboard
                    </Link>
                  </li>
                )}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <Link to="/about" className="hover:text-blue-600">
                    About
                  </Link>
                </li>
                <li>
                  <Link to="/contact" className="hover:text-blue-600">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link to="/enterprise" className="hover:text-blue-600">
                    Enterprise
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <Link to="/legal/privacy" className="hover:text-blue-600">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="/legal/terms" className="hover:text-blue-600">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-6 sm:mt-8 pt-6 sm:pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2025 Trade Scan Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;