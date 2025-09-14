import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { TrendingUp, Activity, Bell, RefreshCw } from 'lucide-react';
import { getMarketStatsSafe, getTrendingSafe } from '../../api/client';

export default function MobileDashboard() {
  const [stats, setStats] = useState(null);
  const [trend, setTrend] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const [s, t] = await Promise.all([getMarketStatsSafe(), getTrendingSafe()]);
    setStats(s.data);
    setTrend(t.data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="p-4 space-y-3">{[...Array(5)].map((_,i)=><div key={i} className="h-10 bg-muted animate-pulse rounded" />)}</div>;

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Mobile Dashboard</h1>
        <Button size="sm" variant="outline" onClick={load}><RefreshCw className="h-4 w-4 mr-1" />Refresh</Button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Card><CardContent className="p-3"><div className="text-xs text-muted-foreground">Gainers</div><div className="text-xl font-semibold text-emerald-600">{stats?.market_overview?.gainers ?? '-'}</div></CardContent></Card>
        <Card><CardContent className="p-3"><div className="text-xs text-muted-foreground">Losers</div><div className="text-xl font-semibold text-red-600">{stats?.market_overview?.losers ?? '-'}</div></CardContent></Card>
        <Card><CardContent className="p-3"><div className="text-xs text-muted-foreground">Total</div><div className="text-xl font-semibold">{stats?.market_overview?.total_stocks ?? '-'}</div></CardContent></Card>
        <Card><CardContent className="p-3"><div className="text-xs text-muted-foreground">Most Active</div><div className="text-xl font-semibold"><Activity className="h-5 w-5" /></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Top Gainers</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(trend?.top_gainers || []).slice(0,5).map((s,i)=> (
            <div key={i} className="flex items-center justify-between text-sm">
              <div className="font-medium">{s.ticker}</div>
              <div className="text-emerald-600 flex items-center gap-1"><TrendingUp className="h-3 w-3" />{(s.change_percent ?? 0).toFixed(1)}%</div>
            </div>
          ))}
          {!(trend?.top_gainers || []).length && <div className="text-sm text-muted-foreground">No data</div>}
        </CardContent>
      </Card>
    </div>
  );
}