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
} from "lucide-react";
import MarketStatus from "../components/MarketStatus";

const AppLayout = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigation = [
    { name: "Home", href: "/", icon: Home },
    { name: "Features", href: "/features", icon: Activity },
    { name: "About", href: "/about", icon: User },
    { name: "Contact", href: "/contact", icon: User },
    { name: "Pricing", href: "/pricing", icon: Crown },
  ];

  const appNavigation = [
    { name: "Dashboard", href: "/app/dashboard", icon: BarChart3 },
    { name: "Markets", href: "/app/markets", icon: TrendingUp },
    { name: "Stocks", href: "/app/stocks", icon: Activity },
    { name: "Screeners", href: "/app/screeners", icon: Search },
    { name: "Portfolio", href: "/app/portfolio", icon: Target },
    { name: "Watchlists", href: "/app/watchlists", icon: Eye },
    { name: "Alerts", href: "/app/alerts", icon: AlertCircle },
    { name: "News", href: "/app/news", icon: Newspaper },
  ];

  const isAppRoute = location.pathname.startsWith("/app");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold text-gray-900">
                Trade Scan Pro
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              {!isAppRoute ? (
                // Public navigation
                <NavigationMenu>
                  <NavigationMenuList>
                    {navigation.map((item) => (
                      <NavigationMenuItem key={item.name}>
                        <Link
                          to={item.href}
                          className={`group inline-flex h-10 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50 ${
                            location.pathname === item.href
                              ? "text-blue-600"
                              : "text-gray-600"
                          }`}
                        >
                          {item.name}
                        </Link>
                      </NavigationMenuItem>
                    ))}
                  </NavigationMenuList>
                </NavigationMenu>
              ) : (
                // App navigation
                <nav className="flex items-center space-x-6">
                  {appNavigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-blue-50 hover:text-blue-600 ${
                          location.pathname === item.href
                            ? "bg-blue-100 text-blue-600"
                            : "text-gray-600"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{item.name}</span>
                      </Link>
                    );
                  })}
                </nav>
              )}
            </div>

            {/* Right side - Auth buttons or user menu */}
            <div className="flex items-center space-x-4">
              {/* Market Status - always show */}
              <div className="hidden lg:block">
                <MarketStatus />
              </div>

              {isAuthenticated && user ? (
                <>
                  {/* User badge */}
                  <Badge variant="secondary" className="hidden sm:inline-flex">
                    {user.plan} Plan
                  </Badge>

                  {/* User menu */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                        <User className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end" forceMount>
                      <div className="flex items-center justify-start gap-2 p-2">
                        <div className="flex flex-col space-y-1 leading-none">
                          <p className="font-medium">{user.name}</p>
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
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={logout}>
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Log out</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </>
              ) : (
                <div className="flex items-center space-x-4">
                  <Button variant="ghost" asChild>
                    <Link to="/auth/sign-in">Sign In</Link>
                  </Button>
                  <Button asChild>
                    <Link to="/auth/sign-up">Get Started for $1</Link>
                  </Button>
                </div>
              )}

              {/* Mobile menu trigger */}
              <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" className="lg:hidden">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                  <nav className="flex flex-col space-y-4">
                    {(isAppRoute ? appNavigation : navigation).map((item) => {
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.name}
                          to={item.href}
                          className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                            location.pathname === item.href
                              ? "bg-blue-100 text-blue-600"
                              : "text-gray-600 hover:bg-gray-100"
                          }`}
                          onClick={() => setIsMobileMenuOpen(false)}
                        >
                          <Icon className="h-4 w-4" />
                          <span>{item.name}</span>
                        </Link>
                      );
                    })}
                  </nav>
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
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <span className="text-xl font-bold">Trade Scan Pro</span>
              </div>
              <p className="text-gray-600">
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
                <li>
                  <Link to="/app/dashboard" className="hover:text-blue-600">
                    Dashboard
                  </Link>
                </li>
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
          <div className="border-t mt-8 pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2025 Trade Scan Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;