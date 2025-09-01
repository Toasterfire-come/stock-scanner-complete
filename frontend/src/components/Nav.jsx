import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { ChartLine, Newspaper, Settings, CreditCard, Activity, Home, LogIn } from 'lucide-react';

const NavItem = ({ to, icon: Icon, label }) => (
  <NavLink to={to} className={({ isActive }) => `inline-flex items-center gap-2 px-3 py-2 rounded-md hover:bg-accent ${isActive ? 'text-primary font-semibold' : 'text-muted-foreground'}`}>
    <Icon className="h-4 w-4" />
    <span className="hidden sm:inline">{label}</span>
  </NavLink>
);

export default function Nav() {
  return (
    <header className="sticky top-0 z-30 w-full border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link to="/" className="font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <span>Stock Scanner</span>
        </Link>
        <nav className="flex items-center gap-1">
          <NavItem to="/app/market" icon={Home} label="Market" />
          <NavItem to="/news" icon={Newspaper} label="News" />
          <NavItem to="/account" icon={Settings} label="Account" />
          <NavItem to="/billing" icon={CreditCard} label="Billing" />
          <NavItem to="/endpoint-status" icon={ChartLine} label="Status" />
          <NavItem to="/auth/login" icon={LogIn} label="Login" />
        </nav>
      </div>
    </header>
  );
}