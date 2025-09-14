import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { getTrending, getMarketStats } from "../api/client";

export default function Markets() {
  const [trending, setTrending] = useState({ high_volume: [], top_gainers: [], most_active: [] });
  const [stats, setStats] = useState(null);
  useEffect(() => {
    getTrending().then(setTrending).catch(() => {});
    getMarketStats().then(setStats).catch(() => {});
  }, []);
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Market overview</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><div className="text-muted-foreground">Total stocks</div><div className="text-xl font-semibold">{stats?.market_overview?.total_stocks ?? "-"}</div></div>
          <div><div className="text-muted-foreground">Gainers</div><div className="text-xl font-semibold text-green-600">{stats?.market_overview?.gainers ?? "-"}</div></div>
          <div><div className="text-muted-foreground">Losers</div><div className="text-xl font-semibold text-red-600">{stats?.market_overview?.losers ?? "-"}</div></div>
          <div><div className="text-muted-foreground">Unchanged</div><div className="text-xl font-semibold">{stats?.market_overview?.unchanged ?? "-"}</div></div>
        </CardContent>
      </Card>
      <div className="grid md:grid-cols-3 gap-4">
        {[{ title: "High Volume", key: "high_volume" }, { title: "Top Gainers", key: "top_gainers" }, { title: "Most Active", key: "most_active" }].map((b) => (
          <Card key={b.key}>
            <CardHeader><CardTitle className="text-base">{b.title}</CardTitle></CardHeader>
            <CardContent className="space-y-2 text-sm">
              {trending[b.key]?.map((it) => (
                <div key={it.ticker} className="flex items-center justify-between">
                  <div className="font-medium">{it.ticker}</div>
                  <div className={it.change_percent > 0 ? "text-green-600" : "text-red-600"}>{it.change_percent?.toFixed?.(2)}%</div>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}