import React, { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  CommandDialog,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandEmpty,
  CommandSeparator
} from "./ui/command";
import { Search, Hash, LayoutDashboard, TrendingUp, Activity, Eye, Target, AlertCircle, Newspaper, FileText, User, Crown } from "lucide-react";

const marketingRoutes = [
  { label: "Home", to: "/", icon: LayoutDashboard },
  { label: "Features", to: "/features", icon: TrendingUp },
  { label: "Pricing", to: "/pricing", icon: Crown },
  { label: "Docs", to: "/docs", icon: FileText },
  { label: "Contact", to: "/contact", icon: Newspaper },
];

const userRoutes = [
  { label: "Dashboard", to: "/app/dashboard", icon: LayoutDashboard },
  { label: "Markets", to: "/app/markets", icon: TrendingUp },
  { label: "Stocks", to: "/app/stocks", icon: Activity },
  { label: "Screeners", to: "/app/screeners", icon: Search },
  { label: "Watchlists", to: "/app/watchlists", icon: Eye },
  { label: "Portfolio", to: "/app/portfolio", icon: Target },
  { label: "Alerts", to: "/app/alerts", icon: AlertCircle },
  { label: "News", to: "/app/news", icon: Newspaper },
  { label: "Exports", to: "/app/exports", icon: FileText },
  { label: "Account", to: "/account/profile", icon: User },
];

export default function CommandPalette({ open, onOpenChange, isAuthenticated = false }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const tickerSuggestion = useMemo(() => {
    const q = (query || "").trim().toUpperCase();
    if (!q) return null;
    // Suggest direct ticker navigation when looks like a symbol
    if (/^[A-Z][A-Z\.-]{0,9}$/.test(q)) return q;
    return null;
  }, [query]);

  const go = useCallback((to) => {
    onOpenChange(false);
    navigate(to);
  }, [navigate, onOpenChange]);

  const goTicker = useCallback(() => {
    if (!tickerSuggestion) return;
    onOpenChange(false);
    navigate(`/app/stocks/${encodeURIComponent(tickerSuggestion)}`);
  }, [navigate, onOpenChange, tickerSuggestion]);

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search… (e.g., AAPL)" value={query} onValueChange={setQuery} />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        {tickerSuggestion && (
          <CommandGroup heading="Quick">
            <CommandItem onSelect={goTicker}>
              <Hash className="mr-2 h-4 w-4" />
              Go to stock {tickerSuggestion}
            </CommandItem>
          </CommandGroup>
        )}
        <CommandGroup heading="Navigate">
          {(isAuthenticated ? [...marketingRoutes, ...userRoutes] : marketingRoutes).map((r) => {
            const Icon = r.icon;
            return (
              <CommandItem key={r.to} onSelect={() => go(r.to)}>
                <Icon className="mr-2 h-4 w-4" />
                {r.label}
              </CommandItem>
            );
          })}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Tips">
          <div className="px-3 py-2 text-xs text-muted-foreground">
            Press Esc to close. Use Up/Down to navigate. Type a ticker like TSLA to jump to it.
          </div>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
