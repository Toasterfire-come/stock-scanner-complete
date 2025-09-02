import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { addWatchlist, getPortfolio, getWatchlist, listStocks } from "../api/client";

export default function AppDashboard() {
  const [stocks, setStocks] = useState([]);
  const [query, setQuery] = useState("");
  const [watchlist, setWatchlist] = useState([]);
  const [portfolio, setPortfolio] = useState([]);

  useEffect(() => {
    listStocks({ limit: 20 }).then((d) => setStocks(d.data || [])).catch(() => {});
    getWatchlist().then((d) => setWatchlist(d.data || [])).catch(() => {});
    getPortfolio().then((d) => setPortfolio(d.data || [])).catch(() => {});
  }, []);

  const addToWatch = async (sym) => {
    const res = await addWatchlist(sym);
    if (res?.success) {
      setWatchlist((w) => [res.data, ...w]);
    }
  };

  const filtered = stocks.filter((s) => !query || s.ticker?.toLowerCase().includes(query.toLowerCase()) || s.company_name?.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search tickers..." />
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>Stocks</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {filtered.map((s) => (
              <div key={s.ticker} className="flex items-center justify-between text-sm border-b py-2">
                <div>
                  <div className="font-medium">{s.ticker} <span className="text-muted-foreground font-normal">{s.company_name}</span></div>
                </div>
                <div className="flex items-center gap-3">
                  <div>${s.current_price}</div>
                  <Button size="sm" onClick={() => addToWatch(s.ticker)}>Watch</Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Watchlist</CardTitle></CardHeader>
            <CardContent className="text-sm space-y-1">
              {watchlist.map((w) => (<div key={w.id} className="flex items-center justify-between"><span>{w.symbol}</span><span className="text-muted-foreground">${w.current_price}</span></div>))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Portfolio</CardTitle></CardHeader>
            <CardContent className="text-sm space-y-1">
              {portfolio.map((p) => (<div key={p.id} className="flex items-center justify-between"><span>{p.symbol}</span><span className="text-muted-foreground">{p.shares} sh</span></div>))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}