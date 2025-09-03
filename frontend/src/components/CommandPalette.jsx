import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
  CommandShortcut,
} from "./ui/command";
import { BarChart3, TrendingUp, Filter, PieChart, Bookmark, AlertTriangle, Newspaper, Home, Zap, Search } from "lucide-react";

export default function CommandPalette({ open, onOpenChange }) {
  const navigate = useNavigate();

  const items = useMemo(() => [
    { label: "Home", to: "/", icon: Home },
    { label: "Dashboard", to: "/app/dashboard", icon: BarChart3 },
    { label: "Markets", to: "/app/markets", icon: TrendingUp },
    { label: "Stocks", to: "/app/stocks", icon: BarChart3 },
    { label: "Screeners", to: "/app/screeners", icon: Filter },
    { label: "Portfolio", to: "/app/portfolio", icon: PieChart },
    { label: "Watchlists", to: "/app/watchlists", icon: Bookmark },
    { label: "Alerts", to: "/app/alerts", icon: AlertTriangle },
    { label: "News", to: "/app/news", icon: Newspaper },
    { label: "Pricing", to: "/pricing", icon: Zap },
  ], []);

  const handleSelect = (to) => {
    onOpenChange(false);
    navigate(to);
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Search pages, tickers, or actions…" autoFocus />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigate">
          {items.map(({ label, to, icon: Icon }) => (
            <CommandItem key={to} onSelect={() => handleSelect(to)}>
              <Icon className="h-4 w-4" />
              <span>{label}</span>
              <CommandShortcut>↵</CommandShortcut>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Search">
          <CommandItem onSelect={() => handleSelect('/app/stocks')}>
            <Search className="h-4 w-4" />
            <span>Search stocks…</span>
            <CommandShortcut>/</CommandShortcut>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}

