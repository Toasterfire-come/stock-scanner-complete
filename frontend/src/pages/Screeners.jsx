import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { listStocks } from "../api/client";

export default function Screeners() {
  const [search, setSearch] = useState(() => { try { return localStorage.getItem('qs_search') || ""; } catch { return ""; } });
  const [minPrice, setMinPrice] = useState(() => { try { return localStorage.getItem('qs_min') || ""; } catch { return ""; } });
  const [maxPrice, setMaxPrice] = useState(() => { try { return localStorage.getItem('qs_max') || ""; } catch { return ""; } });
  const [rows, setRows] = useState([]);

  const run = async () => {
    const params = { limit: 50 };
    if (search) params.search = search;
    if (minPrice) params.min_price = Number(minPrice);
    if (maxPrice) params.max_price = Number(maxPrice);
    const res = await listStocks(params);
    setRows(res.data || []);
  };

  useEffect(() => { run(); }, []);
  useEffect(() => { try { localStorage.setItem('qs_search', search); } catch {} }, [search]);
  useEffect(() => { try { localStorage.setItem('qs_min', minPrice); } catch {} }, [minPrice]);
  useEffect(() => { try { localStorage.setItem('qs_max', maxPrice); } catch {} }, [maxPrice]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Quick Screener</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-5 gap-3 items-end">
          <div className="md:col-span-2"><label className="text-sm">Search</label><Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Ticker or company" /></div>
          <div><label className="text-sm">Min price</label><Input type="number" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} /></div>
          <div><label className="text-sm">Max price</label><Input type="number" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} /></div>
          <div className="text-right"><Button onClick={run}>Run</Button></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Results</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          {rows.map((r) => (
            <div key={r.ticker} className="grid grid-cols-5 gap-2 border-b py-2">
              <div className="font-medium">{r.ticker}</div>
              <div className="col-span-2 text-muted-foreground">{r.company_name}</div>
              <div>${r.current_price}</div>
              <div className={r.change_percent > 0 ? "text-green-600" : "text-red-600"}>{r.change_percent?.toFixed?.(2)}%</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}