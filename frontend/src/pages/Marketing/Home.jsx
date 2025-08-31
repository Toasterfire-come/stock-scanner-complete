import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getTrending, getMarketStats } from "../../lib/api";
import { Link } from "react-router-dom";

export default function Home() {
  const [trending, setTrending] = useState(null);
  const [stats, setStats] = useState(null);
  useEffect(() => {
    getTrending().then((r) => setTrending(r.data)).catch(() => setTrending(null));
    getMarketStats().then((r)=> setStats(r.data)).catch(()=> setStats(null));
  }, []);
  return (
    <Layout>
      <PageHeader
        title="Retail Trade Scanner"
        subtitle="Scan, screen and monitor markets with professional‑grade tools. Create alerts, manage watchlists and stay on top of opportunities."
        cta={<div className="flex gap-3"><Link to="/auth/sign-up" className="btn btn-primary px-4 py-2">Start free</Link><Link to="/features" className="btn btn-secondary px-4 py-2">See features</Link></div>}
      />
      <Section>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {title:'Powerful Screeners',desc:'Filter by price, volume, market cap, fundamentals and more.'},
            {title:'Real-time Alerts',desc:'Get notified when price crosses your target levels.'},
            {title:'Portfolio & Watchlists',desc:'Track positions and monitor symbols in one place.'}
          ].map((f)=> (
            <div key={f.title} className="card p-6">
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </Section>
      <Section className="bg-white dark:bg-[hsl(var(--background))]">
        <h3 className="text-xl font-semibold mb-4">Market highlights</h3>
        {!stats && !trending ? (
          <div className="text-muted-foreground">Loading market data…</div>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {stats?.top_gainers && (
              <div className="card p-4">
                <h4 className="font-medium mb-2">Top gainers</h4>
                <ul className="divide-y">
                  {stats.top_gainers.slice(0,5).map((s) => (
                    <li key={s.ticker} className="py-2 flex items-center justify-between text-sm">
                      <span className="font-medium">{s.ticker}</span>
                      <span className="text-green-600">{s.change_percent?.toFixed?.(2)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {stats?.most_active && (
              <div className="card p-4">
                <h4 className="font-medium mb-2">Most active</h4>
                <ul className="divide-y">
                  {stats.most_active.slice(0,5).map((s) => (
                    <li key={s.ticker} className="py-2 flex items-center justify-between text-sm">
                      <span className="font-medium">{s.ticker}</span>
                      <span className="text-muted-foreground">{s.volume?.toLocaleString?.()}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {trending && (
              <div className="card p-4">
                <h4 className="font-medium mb-2">Trending lists</h4>
                <p className="text-sm text-muted-foreground">Last updated: {new Date(trending.last_updated).toLocaleString?.()}</p>
                <div className="mt-2 text-sm text-muted-foreground">High volume, top gainers and most active fetched from backend.</div>
              </div>
            )}
          </div>
        )}
      </Section>
    </Layout>
  );
}