import React, { useEffect, useState, useMemo } from 'react';
import { endpoints } from '../../lib/api';
import { TrendingUp, TrendingDown, Activity, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export default function MarketOverview() {
  const [state, setState] = useState({ loading: true, error: '', stats: null, trending: null });

  const load = async () => {
    setState(s => ({ ...s, loading: true, error: '' }));
    const [stats, trending] = await Promise.all([
      endpoints.stocks.marketStats(),
      endpoints.stocks.trending(),
    ]);
    const error = (!stats.ok && stats.error) || (!trending.ok && trending.error);
    if (error) {
      setState({ loading: false, error, stats: stats.data || null, trending: trending.data || null });
      toast.error(`Market data failed: ${error}`);
    } else {
      setState({ loading: false, error: '', stats: stats.data, trending: trending.data });
    }
  };

  useEffect(() => { load(); }, []);

  const overview = state.stats?.market_overview;
  const gainers = state.trending?.top_gainers || [];
  const mostActive = state.trending?.most_active || [];

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Market Overview</h1>
        <button onClick={load} className="inline-flex items-center gap-2 px-3 py-2 rounded-md border hover:bg-accent">
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {state.loading && <Skeleton />}
      {!state.loading && state.error && (
        <div className="p-4 border rounded bg-destructive/10 text-destructive">{state.error}</div>
      )}

      {!state.loading && !state.error && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Metric label="Total" value={overview?.total_stocks ?? '-'} icon={Activity} />
            <Metric label="Gainers" value={overview?.gainers ?? '-'} positive />
            <Metric label="Losers" value={overview?.losers ?? '-'} negative />
            <Metric label="Unchanged" value={overview?.unchanged ?? '-'} />
          </div>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">Top Gainers</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              {gainers.map((s, i) => <StockCard key={i} s={s} positive />)}
              {!gainers.length && <Empty label="No gainers available" />}
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-medium">Most Active</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              {mostActive.map((s, i) => <StockCard key={i} s={s} />)}
              {!mostActive.length && <Empty label="No most active data" />}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-muted animate-pulse rounded" />)}
      </div>
      <div className="h-8 w-40 bg-muted animate-pulse rounded" />
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {[...Array(6)].map((_, i) => <div key={i} className="h-24 bg-muted animate-pulse rounded" />)}
      </div>
    </div>
  );
}

function Metric({ label, value, positive, negative, icon: Icon }) {
  return (
    <div className="p-4 border rounded">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-2xl font-semibold flex items-center gap-2">
        {positive && <TrendingUp className="h-5 w-5 text-emerald-600" />}
        {negative && <TrendingDown className="h-5 w-5 text-red-600" />}
        {!positive && !negative && Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
        <span>{value}</span>
      </div>
    </div>
  );
}

function StockCard({ s, positive }) {
  const pct = s.change_percent ?? s.price_change_today ?? 0;
  const isUp = (pct || 0) >= 0;
  return (
    <div className="p-4 border rounded">
      <div className="flex items-center justify-between">
        <div className="font-medium">{s.ticker || s.symbol}</div>
        <div className={`text-sm ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>{pct?.toFixed ? pct.toFixed(2) : pct}%</div>
      </div>
      <div className="text-sm text-muted-foreground">{s.name || s.company_name || '-'}</div>
      <div className="text-sm mt-1">${(s.current_price ?? 0).toLocaleString()}</div>
    </div>
  );
}

function Empty({ label }) {
  return <div className="p-4 border rounded text-center text-muted-foreground">{label}</div>;
}