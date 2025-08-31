import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getTrending } from "../../lib/api";
import { Link } from "react-router-dom";

export default function Home() {
  const [trending, setTrending] = useState(null);
  useEffect(() => {
    getTrending().then((r) => setTrending(r.data)).catch(() => setTrending(null));
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
      <Section className="bg-white">
        <h3 className="text-xl font-semibold mb-4">Market highlights</h3>
        {!trending ? (
          <div className="text-muted-foreground">Loading market data…</div>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {Object.entries(trending).filter(([k])=>k!=="last_updated").map(([key, list]) => (
              <div key={key} className="card p-4">
                <h4 className="font-medium mb-2 capitalize">{key.replace('_',' ')}</h4>
                <ul className="divide-y">
                  {(list || []).slice(0,5).map((s) => (
                    <li key={s.ticker} className="py-2 flex items-center justify-between text-sm">
                      <span className="font-medium">{s.ticker}</span>
                      <span className={s.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}>{s.change_percent?.toFixed?.(2)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </Section>
    </Layout>
  );
}