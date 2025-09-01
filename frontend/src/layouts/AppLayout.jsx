import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Home, LayoutDashboard, Bell, ListTree, LineChart, Wallet, BellRing, Globe, CreditCard, LogIn, LogOut, ShieldCheck, Settings } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Separator } from "../components/ui/separator";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Home", icon: Home },
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/markets", label: "Markets", icon: Globe },
  { to: "/app/screeners", label: "Screeners", icon: ListTree },
  { to: "/app/portfolio", label: "Portfolio", icon: Wallet },
  { to: "/app/alerts", label: "Alerts", icon: BellRing },
  { to: "/app/notifications", label: "Notifications", icon: Bell },
  { to: "/pricing", label: "Pricing", icon: CreditCard },
  { to: "/status", label: "Status", icon: ShieldCheck },
  { to: "/legal/terms", label: "Terms", icon: ShieldCheck },
  { to: "/legal/privacy", label: "Privacy", icon: Settings },
];

function Sidebar({ expanded }) {
  return (
    <aside className={`h-screen sticky top-0 border-r bg-card ${expanded ? "w-60" : "w-16"} transition-[width] duration-200`}> 
      <div className="p-2 flex items-center gap-2 h-14">
        <LineChart className="w-6 h-6" />
        {expanded && <span className="font-semibold">Retail Trade Scanner</span>}
      </div>
      <Separator />
      <nav className="p-2 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent ${isActive ? "bg-accent font-medium" : ""}`}>
            <Icon className="w-4 h-4" />
            {expanded && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

function Header({ onToggleSidebar, expanded }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <header className="h-14 border-b flex items-center justify-between px-4 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10">
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={onToggleSidebar}><Home className="w-4 h-4" /></Button>
        <span className="font-medium">{expanded ? "Collapse" : "Expand"} menu</span>
      </div>
      <div className="flex items-center gap-2">
        {!user ? (
          <>
            <Button size="sm" variant="outline" onClick={() => navigate("/auth/sign-in")}>Sign in</Button>
            <Button size="sm" onClick={() => navigate("/pricing")}>Sign up</Button>
          </>
        ) : (
          <>
            <Button size="sm" variant="default" onClick={() => navigate("/pricing")}>Upgrade</Button>
            <Button size="sm" variant="ghost" onClick={logout}><LogOut className="w-4 h-4" /></Button>
          </>
        )}
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="border-t py-8 px-6 bg-card/50 mt-10">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
        <div>
          <div className="font-semibold mb-2">Product</div>
          <ul className="space-y-1">
            <li><NavLink to="/features">Features</NavLink></li>
            <li><NavLink to="/product">Overview</NavLink></li>
            <li><NavLink to="/pricing">Pricing</NavLink></li>
            <li><NavLink to="/data">Data coverage</NavLink></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">Resources</div>
          <ul className="space-y-1">
            <li><NavLink to="/status">System status</NavLink></li>
            <li><NavLink to="/docs">Docs</NavLink></li>
            <li><NavLink to="/help">Help center</NavLink></li>
            <li><NavLink to="/contact">Contact</NavLink></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">Company</div>
          <ul className="space-y-1">
            <li><NavLink to="/about">About</NavLink></li>
            <li><NavLink to="/careers">Careers</NavLink></li>
            <li><NavLink to="/community">Community</NavLink></li>
            <li><NavLink to="/roadmap">Roadmap</NavLink></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">Legal</div>
          <ul className="space-y-1">
            <li><NavLink to="/legal/terms">Terms</NavLink></li>
            <li><NavLink to="/legal/privacy">Privacy</NavLink></li>
          </ul>
        </div>
      </div>
      <div className="text-xs text-muted-foreground mt-6">© {new Date().getFullYear()} Retail Trade Scanner. All rights reserved.</div>
    </footer>
  );
}

export default function AppLayout() {
  const [expanded, setExpanded] = useState(true);
  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <Sidebar expanded={expanded} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header expanded={expanded} onToggleSidebar={() => setExpanded((s) => !s)} />
        <main className="p-4 md:p-6 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}