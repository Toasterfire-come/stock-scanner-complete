import React, { useMemo, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getStocks } from "../../lib/api";

export default function Screeners(){
  const [q, setQ] = useState({ search:"", category:"all", exchange:"", min_price:"", max_price:"", min_volume:"", min_market_cap:"", max_market_cap:"", min_pe:"", max_pe:"", sort_by:"last_updated", sort_order:"desc", limit: 50 });
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(() => {
    const p = { ...q };
    Object.keys(p).forEach(k => { if (p[k] === "" || p[k] === null) delete p[k]; });
    return p;
  }, [q]);

  async function run(){
    setLoading(true); setError("");
    try {
      const r = await getStocks(params);
      setRows(r.data?.data || r.data?.stocks || []);
    } catch (e){ setError("Failed to fetch stocks"); }
    finally { setLoading(false); }
  }

  return (
    <Layout>
      <PageHeader title="Stock Scanner" subtitle="Filter and search stocks with advanced criteria." />
      <Section>
        <div className="card p-6">
          <div className="grid md:grid-cols-3 gap-4">
            <input className="input" placeholder="Search (ticker or company)" value={q.search} onChange={(e)=> setQ({...q, search:e.target.value})} />
            <select className="input" value={q.category} onChange={(e)=> setQ({...q, category:e.target.value})}>
              <option value="all">Any Category</option>
              <option value="gainers">Gainers</option>
              <option value="losers">Losers</option>
              <option value="high_volume">High Volume</option>
              <option value="large_cap">Large Cap</option>
              <option value="small_cap">Small Cap</option>
            </select>
            <input className="input" placeholder="Exchange (or all)" value={q.exchange} onChange={(e)=> setQ({...q, exchange:e.target.value})} />
            <input className="input" placeholder="Min Price" type="number" value={q.min_price} onChange={(e)=> setQ({...q, min_price:e.target.value})} />
            <input className="input" placeholder="Max Price" type="number" value={q.max_price} onChange={(e)=> setQ({...q, max_price:e.target.value})} />
            <input className="input" placeholder="Min Volume" type="number" value={q.min_volume} onChange={(e)=> setQ({...q, min_volume:e.target.value})} />
            <input className="input" placeholder="Min Market Cap" type="number" value={q.min_market_cap} onChange={(e)=> setQ({...q, min_market_cap:e.target.value})} />
            <input className="input" placeholder="Max Market Cap" type="number" value={q.max_market_cap} onChange={(e)=> setQ({...q, max_market_cap:e.target.value})} />
            <input className="input" placeholder="Min P/E" type="number" step="0.01" value={q.min_pe} onChange={(e)=> setQ({...q, min_pe:e.target.value})} />
            <input className="input" placeholder="Max P/E" type="number" step="0.01" value={q.max_pe} onChange={(e)=> setQ({...q, max_pe:e.target.value})} />
            <select className="input" value={q.sort_by} onChange={(e)=> setQ({...q, sort_by:e.target.value})}>
              <option value="last_updated">Sort: Last Updated</option>
              <option value="price">Sort: Price</option>
              <option value="volume">Sort: Volume</option>
              <option value="market_cap">Sort: Market Cap</option>
              <option value="change_percent">Sort: Change %</option>
            </select>
            <select className="input" value={q.sort_order} onChange={(e)=> setQ({...q, sort_order:e.target.value})}>
              <option value="desc">Desc</option>
              <option value="asc">Asc</option>
            </select>
            <input className="input" placeholder="Limit (<=1000)" type="number" value={q.limit} onChange={(e)=> setQ({...q, limit:Number(e.target.value)})} />
            <button className="btn btn-primary py-2" onClick={run} disabled={loading}>{loading? 'Running…' : 'Run'}</button>
          </div>
          {error && <div className="mt-4 text-red-600 text-sm">{error}</div>}
        </div>
      </Section>
      <Section>
        <div className="card p-6">
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b border-border">
                  <th className="py-2">Ticker</th>
                  <th className="py-2">Company</th>
                  <th className="py-2">Price</th>
                  <th className="py-2">Change%</th>
                  <th className="py-2">Volume</th>
                  <th className="py-2">Market Cap</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr><td colSpan="6" className="py-6 text-center text-muted-foreground">No results</td></tr>
                ) : rows.map(s => (
                  <tr key={s.ticker} className="border-b border-border/70">
                    <td className="py-2 font-medium">{s.ticker || s.symbol}</td>
                    <td className="py-2">{s.company_name || s.name}</td>
                    <td className="py-2">{s.current_price}</td>
                    <td className={`py-2 ${s.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>{s.change_percent}</td>
                    <td className="py-2">{s.volume?.toLocaleString?.()}</td>
                    <td className="py-2">{s.market_cap?.toLocaleString?.()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Section>
    </Layout>
  );
}