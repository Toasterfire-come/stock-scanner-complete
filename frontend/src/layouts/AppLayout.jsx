import React, { useEffect, useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator } from "../components/ui/breadcrumb";
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
  Sheet,
  SheetContent,
  SheetTrigger,
} from "../components/ui/sheet";
import {
  BarChart3,
  TrendingUp,
  Search,
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
import ThemeToggle from "../components/ThemeToggle";
import SearchDialog from "../components/SearchDialog";
import ShortcutsHelp from "../components/ShortcutsHelp";
import { Link as RouterLink } from "react-router-dom";
import { useEffect as ReactUseEffect } from "react";
import { api } from "../api/client";

const AppLayout = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  const [unreadAlerts, setUnreadAlerts] = useState(0);
  const [unreadNews, setUnreadNews] = useState(0);
  // Global keyboard shortcut: Ctrl+K / Cmd+K opens search
  useEffect(() => {
    const onKeyDown = (e) => {
      const isK = (e.key || '').toLowerCase() === 'k';
      if (isK && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        setIsSearchOpen(true);
      }
      if ((e.key || '') === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        setIsShortcutsOpen(true);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  // Poll unread counts when authenticated
  useEffect(() => {
    let timer;
    async function fetchUnread() {
      if (!isAuthenticated) { setUnreadAlerts(0); setUnreadNews(0); return; }
      try {
        const [alertsRes, newsRes] = await Promise.all([
          api.get('/alerts/unread-count/').catch(()=>({ data:{ count:0 }})),
          api.get('/news/unread-count/').catch(()=>({ data:{ count:0 }}))
        ]);
        setUnreadAlerts(Number(alertsRes?.data?.count || 0));
        setUnreadNews(Number(newsRes?.data?.count || 0));
      } catch {}
    }
    fetchUnread();
    timer = setInterval(fetchUnread, 60000);
    return () => { if (timer) clearInterval(timer); };
  }, [isAuthenticated]);

  const marketingPages = [
    { name: "Home", href: "/", icon: Home },
    { name: "Features", href: "/features", icon: Activity },
    { name: "About", href: "/about", icon: User },
    { name: "Contact", href: "/contact", icon: User },
    { name: "Pricing", href: "/pricing", icon: Crown },
  ];

  const appPages = [
    { name: "Dashboard", href: "/app/dashboard", icon: BarChart3 },
    { name: "Markets", href: "/app/markets", icon: TrendingUp },
    { name: "Stocks", href: "/app/stocks", icon: Activity },
    { name: "Screeners", href: "/app/screeners", icon: Search },
    { name: "Portfolio", href: "/app/portfolio", icon: Target },
    { name: "Watchlists", href: "/app/watchlists", icon: Eye },
    { name: "Alerts", href: "/app/alerts", icon: AlertCircle },
    { name: "News", href: "/app/news", icon: Newspaper },
  ];

  const segments = (location.pathname || '/').split('/').filter(Boolean);
  const crumbs = segments.map((seg, idx) => {
    const path = '/' + segments.slice(0, idx + 1).join('/');
    const label = seg.replace(/[-_]/g, ' ');
    return { path, label };
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Skip link for keyboard users */}
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 bg-blue-600 text-white px-3 py-2 rounded">Skip to main content</a>
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-14 sm:h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
              <BarChart3 className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              <span className="text-lg sm:text-2xl font-bold text-gray-900 dark:text-gray-100 hidden sm:block">Trade Scan Pro</span>
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100 sm:hidden">TSP</span>
            </Link>

            {/* Spacer */}
            <div className="flex-1" />

            {/* Right side controls */}
            <div className="flex items-center space-x-2 sm:space-x-3">
              {/* Market Status */}
              <div className="hidden md:block">
                <MarketStatus />
              </div>

              {/* Theme toggle */}
              <ThemeToggle />

              {/* Search trigger */}
              <Button
                variant="ghost"
                className="hidden md:inline-flex h-9 px-3 rounded-md text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
                aria-label="Open search (Ctrl+K)"
                onClick={() => setIsSearchOpen(true)}
              >
                <Search className="h-4 w-4 mr-2" />
                <span className="hidden lg:inline">Search</span>
                <kbd className="ml-2 rounded bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 text-xs text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700">Ctrl K</kbd>
              </Button>

              {/* Alerts */}
              <Button asChild variant="ghost" className="hidden md:inline-flex h-9 px-3 rounded-md relative">
                <RouterLink to="/app/alerts" aria-label="Alerts">
                  <AlertCircle className="h-4 w-4" />
                  {isAuthenticated && unreadAlerts > 0 && (
                    <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-red-600 text-white">
                      {unreadAlerts > 99 ? '99+' : unreadAlerts}
                    </span>
                  )}
                </RouterLink>
              </Button>

              {/* News */}
              <Button asChild variant="ghost" className="hidden md:inline-flex h-9 px-3 rounded-md relative">
                <RouterLink to="/app/news" aria-label="News">
                  <Newspaper className="h-4 w-4" />
                  {isAuthenticated && unreadNews > 0 && (
                    <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-blue-600 text-white">
                      {unreadNews > 99 ? '99+' : unreadNews}
                    </span>
                  )}
                </RouterLink>
              </Button>

              {/* Hamburger menu - visible across all sizes */}
              <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" className="h-9 w-9 p-0 rounded-md" aria-label="Open navigation">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[280px] sm:w-[350px]">
                  <div className="mt-6">
                    <div className="mb-6 md:hidden">
                      <MarketStatus />
                    </div>
                    <nav className="flex flex-col space-y-3" role="navigation" aria-label="Primary">
                      {/* App pages only when authenticated */}
                      {isAuthenticated && (
                        <>
                          <div className="text-xs text-muted-foreground font-medium uppercase pt-2">App</div>
                          {appPages.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.href;
                            return (
                              <Link
                                key={item.name}
                                to={item.href}
                                aria-current={isActive ? 'page' : undefined}
                                className={`flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-colors ${
                                  isActive
                                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-950/50 dark:text-blue-300'
                                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                                }`}
                                onClick={() => setIsMobileMenuOpen(false)}
                              >
                                <Icon className="h-5 w-5" />
                                <span>{item.name}</span>
                              </Link>
                            );
                          })}
                        </>
                      )}

                      {/* Marketing pages below app pages */}
                      <div className="text-xs text-muted-foreground font-medium uppercase pt-4">Marketing</div>
                      {marketingPages.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.href;
                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                            aria-current={isActive ? 'page' : undefined}
                            className={`flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-colors ${
                              isActive
                                ? 'bg-blue-100 text-blue-600 dark:bg-blue-950/50 dark:text-blue-300'
                                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                            }`}
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            <Icon className="h-5 w-5" />
                            <span>{item.name}</span>
                          </Link>
                        );
                      })}

                      {/* Mobile auth buttons for guests */}
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

              {/* Auth or user menu */}
              {isAuthenticated && user ? (
                <>
                  <Badge variant="secondary" className="hidden sm:inline-flex text-xs">
                    {String(user.plan || '').charAt(0).toUpperCase() + String(user.plan || '').slice(1)} Plan
                  </Badge>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-8 w-8 rounded-full" aria-label="User menu">
                        <User className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end" forceMount>
                      <div className="flex items-center justify-start gap-2 p-2">
                        <div className="flex flex-col space-y-1 leading-none">
                          <p className="font-medium">{user.name}</p>
                          <p className="w-[200px] truncate text-sm text-muted-foreground">{user.email}</p>
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
                <div className="hidden md:flex items-center space-x-2 sm:space-x-3">
                  <Button variant="ghost" asChild className="hidden sm:inline-flex">
                    <Link to="/auth/sign-in">Sign In</Link>
                  </Button>
                  <Button asChild size="sm" className="text-sm px-3 sm:px-4">
                    <Link to="/auth/sign-up">Try Now for Free</Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main id="main-content">
        <div className="container mx-auto px-4 py-2">
          {segments.length > 0 && (
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink asChild>
                    <Link to="/">Home</Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                {crumbs.map((c, i) => (
                  <React.Fragment key={c.path}>
                    <BreadcrumbSeparator />
                    <BreadcrumbItem>
                      {i === crumbs.length - 1 ? (
                        <BreadcrumbPage>{c.label}</BreadcrumbPage>
                      ) : (
                        <BreadcrumbLink asChild>
                          <Link to={c.path}>{c.label}</Link>
                        </BreadcrumbLink>
                      )}
                    </BreadcrumbItem>
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          )}
        </div>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8 sm:py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <span className="text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100">Trade Scan Pro</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                Professional stock screening and market intelligence platform.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link to="/features" className="hover:text-blue-600">Features</Link></li>
                <li><Link to="/pricing" className="hover:text-blue-600">Pricing</Link></li>
                <li><Link to="/app/dashboard" className="hover:text-blue-600">Dashboard</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link to="/about" className="hover:text-blue-600">About</Link></li>
                <li><Link to="/contact" className="hover:text-blue-600">Contact</Link></li>
                <li><Link to="/enterprise" className="hover:text-blue-600">Enterprise</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link to="/legal/privacy" className="hover:text-blue-600">Privacy Policy</Link></li>
                <li><Link to="/legal/terms" className="hover:text-blue-600">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-6 sm:mt-8 pt-6 sm:pt-8 text-center text-sm text-gray-600 dark:text-gray-400">
            <p>&copy; 2025 Trade Scan Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Dialogs */}
      <SearchDialog open={isSearchOpen} onOpenChange={setIsSearchOpen} />
      <ShortcutsHelp open={isShortcutsOpen} onOpenChange={setIsShortcutsOpen} />
    </div>
  );
};

export default AppLayout;