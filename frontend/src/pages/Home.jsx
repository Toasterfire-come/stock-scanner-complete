import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { getTrending, getMarketStats } from "../api/client";

export default function Home() {
  const navigate = useNavigate();
  const [trending, setTrending] = useState({ high_volume: [], top_gainers: [], most_active: [] });
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    getTrending().then(setTrending).catch(() => {});
    getMarketStats().then(setOverview).catch(() => {});
  }, []);

  return (
    <div className="space-y-10">
      <section className="rounded-2xl border bg-card overflow-hidden">
        <div className="p-8 md:p-12 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <h1 className="text-3xl md:text-4xl font-semibold leading-tight">Retail Trade Scanner</h1>
            <p className="mt-3 text-muted-foreground">Powerful stock screeners, alerts and market insights built for active retail traders.</p>
            <div className="mt-6 flex flex-wrap gap-3 items-center">
              <Button onClick={() => navigate("/pricing?code=trial")} className="">Start Trial for $1</Button>
              <span className="text-sm text-muted-foreground">7-day trial • then auto-renews at full price • Cancel anytime</span>
            </div>
            <div className="mt-4">
              <Badge variant="secondary">Promo code</Badge> <Badge>trial</Badge>
            </div>
          </div>
          <div className="bg-accent/50 rounded-xl p-6">
            <div className="grid grid-cols-3 gap-4">
              {overview?.top_gainers?.map((g) => (
                <Card key={g.ticker} className="bg-background">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">{g.ticker}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-xs text-muted-foreground">
                    <div>${g.current_price?.toFixed?.(2) ?? g.current_price}</div>
                    <div className={g.change_percent > 0 ? "text-green-600" : "text-red-600"}>{g.change_percent?.toFixed?.(2)}%</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">Trending</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[{ title: "High Volume", key: "high_volume" }, { title: "Top Gainers", key: "top_gainers" }, { title: "Most Active", key: "most_active" }].map((b) => (
            <Card key={b.key}>
              <CardHeader><CardTitle className="text-base">{b.title}</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {trending[b.key]?.map((it) => (
                    <div key={it.ticker} className="flex items-center justify-between text-sm">
                      <div className="font-medium">{it.ticker}</div>
                      <div className="text-muted-foreground">{it.change_percent?.toFixed?.(2)}%</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}