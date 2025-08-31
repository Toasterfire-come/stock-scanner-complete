import React, { useEffect, useState } from "react";
import GenericPage from "./GenericPage";
import { getStatistics } from "../../lib/api";

export default function Docs(){
  const [stats, setStats] = useState(null);
  useEffect(()=>{ getStatistics().then(r=> setStats(r.data)).catch(()=> setStats(null)); },[]);
  return (
    <GenericPage title="Documentation" subtitle="API and product documentation.">
      <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
        <li>REST API base: <code>/api/</code></li>
        <li>Stocks: <code>/api/stocks/</code></li>
        <li>Search: <code>/api/search/</code></li>
        <li>Trending: <code>/api/trending/</code></li>
        <li>Alerts: <code>/api/alerts/create/</code></li>
      </ul>
      {stats && (
        <div className="card p-4 mt-6">
          <div className="text-sm text-muted-foreground">Live sample</div>
          <div className="mt-1 text-sm">Total stocks: <span className="font-medium">{stats.market_overview?.total_stocks}</span></div>
          <div className="mt-1 text-sm">Gainers: <span className="text-green-600 font-medium">{stats.market_overview?.gainers}</span> • Losers: <span className="text-red-600 font-medium">{stats.market_overview?.losers}</span></div>
        </div>
      )}
    </GenericPage>
  );
}