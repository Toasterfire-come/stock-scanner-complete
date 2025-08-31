import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { subscribeEmail } from "../lib/api";
import { toast } from "sonner";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
  { to: "/pricing", label: "Pricing" },
  { to: "/data", label: "Data" },
  { to: "/docs", label: "Docs" },
  { to: "/app/alerts", label: "Alerts" },
  { to: "/design-system", label: "Design" },
];

function Navbar() {
  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-white/80 dark:bg-[hsl(var(--background))]/80 border-b border-border">
      <div className="container-page h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[hsl(var(--accent))]"></div>
          <span className="font-semibold">Retail Trade Scanner</span>
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((n) => (
            <NavLink key={n.to} to={n.to} className={({isActive}) => `text-sm ${isActive ? 'text-[hsl(var(--accent))] font-medium' : 'text-muted-foreground hover:text-foreground'}`}>{n.label}</NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link to="/auth/sign-in" className="btn btn-outline px-3 py-2">Sign in</Link>
          <Link to="/auth/sign-up" className="btn btn-primary px-3 py-2">Get started</Link>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  const [email, setEmail] = useState("");
  async function subscribe(e){
    e.preventDefault();
    try { await subscribeEmail({ email }); toast.success("Subscribed"); setEmail(""); }
    catch { toast.error("Subscription failed"); }
  }
  return (
    <footer className="mt-20 border-t border-border bg-white dark:bg-[hsl(var(--background))]">
      <div className="container-page py-12 grid grid-cols-1 md:grid-cols-4 gap-10">
        <div>
          <h4 className="text-lg font-semibold mb-2">Retail Trade Scanner</h4>
          <p className="text-sm text-muted-foreground">Professional stock screening, alerts and portfolio tools for serious traders.</p>
          <form onSubmit={subscribe} className="mt-4 flex gap-2">
            <input className="input" placeholder="Enter your email" value={email} onChange={(e)=> setEmail(e.target.value)} required />
            <button className="btn btn-secondary px-3">Subscribe</button>
          </form>
        </div>
        <div>
          <h5 className="font-semibold mb-2">Product</h5>
          <ul className="space-y-1 text-sm">
            <li><Link to="/features" className="hover:text-foreground text-muted-foreground">Features</Link></li>
            <li><Link to="/pricing" className="hover:text-foreground text-muted-foreground">Pricing</Link></li>
            <li><Link to="/use-cases" className="hover:text-foreground text-muted-foreground">Use cases</Link></li>
          </ul>
        </div>
        <div>
          <h5 className="font-semibold mb-2">Resources</h5>
          <ul className="space-y-1 text-sm">
            <li><Link to="/docs" className="hover:text-foreground text-muted-foreground">Docs</Link></li>
            <li><Link to="/guides" className="hover:text-foreground text-muted-foreground">Guides</Link></li>
            <li><Link to="/tutorials" className="hover:text-foreground text-muted-foreground">Tutorials</Link></li>
          </ul>
        </div>
        <div>
          <h5 className="font-semibold mb-2">Legal</h5>
          <ul className="space-y-1 text-sm">
            <li><Link to="/legal/terms" className="hover:text-foreground text-muted-foreground">Terms</Link></li>
            <li><Link to="/legal/privacy" className="hover:text-foreground text-muted-foreground">Privacy</Link></li>
            <li><Link to="/legal/security" className="hover:text-foreground text-muted-foreground">Security</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border">
        <div className="container-page py-6 text-xs text-muted-foreground flex items-center justify-between">
          <span>© {new Date().getFullYear()} Retail Trade Scanner. All rights reserved.</span>
          <span>Trading involves risk. Past performance is not indicative of future results.</span>
        </div>
      </div>
    </footer>
  );
}

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-[hsl(var(--background))]">
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}