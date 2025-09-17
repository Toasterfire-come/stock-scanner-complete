import React from "react";
import { useNavigate } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Command, CommandInput, CommandList, CommandGroup, CommandItem, CommandEmpty } from "./ui/command";
import { searchStocks, getTrendingSafe } from "../api/client";
import { Search } from "lucide-react";

const PAGE_LINKS = [
  { name: 'Dashboard', path: '/app/dashboard', group: 'App' },
  { name: 'Markets', path: '/app/markets', group: 'App' },
  { name: 'Stocks', path: '/app/stocks', group: 'App' },
  { name: 'Screeners', path: '/app/screeners', group: 'App' },
  { name: 'Portfolio', path: '/app/portfolio', group: 'App' },
  { name: 'Watchlists', path: '/app/watchlists', group: 'App' },
  { name: 'Alerts', path: '/app/alerts', group: 'App' },
  { name: 'News', path: '/app/news', group: 'App' },
  { name: 'Pricing', path: '/pricing', group: 'Marketing' },
  { name: 'Features', path: '/features', group: 'Marketing' },
  { name: 'About', path: '/about', group: 'Marketing' },
  { name: 'Contact', path: '/contact', group: 'Marketing' },
];

function scoreResult(query, item, trendingTickersSet) {
  const q = (query || '').trim().toLowerCase();
  if (!q) return 0;
  let text = '';
  if (item.type === 'page') text = item.name;
  if (item.type === 'stock') text = `${item.ticker} ${item.name || ''}`;
  const t = text.toLowerCase();
  let score = 0;
  if (t === q) score += 100;
  if (t.startsWith(q)) score += 80;
  if (t.includes(q)) score += 50;
  // Prefer exact ticker matches
  if (item.type === 'stock') {
    const tk = (item.ticker || '').toLowerCase();
    if (tk === q) score += 120;
    if (tk.startsWith(q)) score += 90;
    if (trendingTickersSet && trendingTickersSet.has(item.ticker)) score += 15;
  }
  // Slight boost to app pages
  if (item.type === 'page' && item.group === 'App') score += 10;
  return score;
}

export default function SearchDialog({ open, onOpenChange }) {
  const navigate = useNavigate();
  const inputRef = React.useRef(null);
  const [query, setQuery] = React.useState('');
  const [results, setResults] = React.useState([]);
  const [activeIndex, setActiveIndex] = React.useState(0);
  const [trendingSet, setTrendingSet] = React.useState(null);

  React.useEffect(() => {
    if (!open) return;
    const t = setTimeout(() => { try { inputRef.current?.focus(); } catch {} }, 50);
    return () => clearTimeout(t);
  }, [open]);

  React.useEffect(() => {
    let mounted = true;
    (async () => {
      const { success, data } = await getTrendingSafe();
      if (!mounted) return;
      if (success) {
        const tickers = new Set([
          ...(data?.high_volume || []).map(s => s.ticker),
          ...(data?.top_gainers || []).map(s => s.ticker),
          ...(data?.most_active || []).map(s => s.ticker),
        ]);
        setTrendingSet(tickers);
      }
    })();
    return () => { mounted = false; };
  }, []);

  React.useEffect(() => {
    let cancelled = false;
    async function run() {
      const trimmed = query.trim();
      const pages = PAGE_LINKS
        .filter(p => p.name.toLowerCase().includes(trimmed.toLowerCase()))
        .map(p => ({ type: 'page', name: p.name, path: p.path, group: p.group }));

      if (!trimmed) {
        setResults(pages);
        setActiveIndex(0);
        return;
      }
      try {
        const stocks = await searchStocks(trimmed);
        const stockItems = (Array.isArray(stocks) ? stocks : (stocks?.results || stocks?.data || []))
          .slice(0, 25)
          .map(s => ({ type: 'stock', ticker: s.symbol || s.ticker || '-', name: s.name || s.company_name || '' }));

        const combined = [...stockItems, ...pages];
        const ranked = combined
          .map(item => ({ item, score: scoreResult(trimmed, item, trendingSet) }))
          .sort((a, b) => b.score - a.score)
          .map(x => x.item)
          .slice(0, 25);
        if (!cancelled) {
          setResults(ranked);
          setActiveIndex(0);
        }
      } catch {
        if (!cancelled) {
          setResults(pages);
          setActiveIndex(0);
        }
      }
    }
    const id = setTimeout(run, 200);
    return () => { cancelled = true; clearTimeout(id); };
  }, [query, trendingSet]);

  function onSelect(item) {
    if (item.type === 'page') {
      navigate(item.path);
      onOpenChange(false);
      return;
    }
    if (item.type === 'stock') {
      navigate(`/app/stocks/${encodeURIComponent(item.ticker)}`);
      onOpenChange(false);
      return;
    }
  }

  function onKeyDown(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActiveIndex(i => Math.min(i + 1, results.length - 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActiveIndex(i => Math.max(i - 1, 0)); }
    if (e.key === 'Enter') { e.preventDefault(); const item = results[activeIndex]; if (item) onSelect(item); }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent aria-label="Search" className="p-0 overflow-hidden">
        <DialogHeader className="sr-only">
          <DialogTitle>Search</DialogTitle>
        </DialogHeader>
        <div role="search" aria-label="Site search">
          <Command onKeyDown={onKeyDown}>
            <div className="flex items-center border-b px-3">
              <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search stocks and pages..."
                aria-label="Search stocks and pages"
                className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground"
              />
            </div>
            <CommandList role="listbox" aria-label="Search results">
              {results.length === 0 && (
                <CommandEmpty>No results</CommandEmpty>
              )}
              <CommandGroup heading="Results">
                {results.map((item, idx) => (
                  <CommandItem
                    key={item.type === 'page' ? item.path : item.ticker}
                    role="option"
                    aria-selected={idx === activeIndex}
                    className={idx === activeIndex ? 'bg-accent text-accent-foreground' : ''}
                    onMouseEnter={() => setActiveIndex(idx)}
                    onClick={() => onSelect(item)}
                  >
                    {item.type === 'page' ? (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">{item.group}</span>
                        <span className="font-medium">{item.name}</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-semibold">{item.ticker}</span>
                        <span className="text-muted-foreground">{item.name}</span>
                      </div>
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </div>
      </DialogContent>
    </Dialog>
  );
}

