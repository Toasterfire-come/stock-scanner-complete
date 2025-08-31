import React, { useMemo, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getStocks } from "../../lib/api";
import Pagination from "../../components/Pagination";
import SortHeader from "../../components/SortHeader";
import AutosuggestSearch from "../../components/AutosuggestSearch";
import { TableSkeleton } from "../../components/Skeletons";
import Badge from "../../components/Badge";
import { toast } from "sonner";

export default function Screeners(){
  const [q, setQ] = useState({ search:"", category:"all", exchange:"", min_price:"", max_price:"", min_volume:"", min_market_cap:"", max_market_cap:"", min_pe:"", max_pe:"", sort_by:"last_updated", sort_order:"desc", limit: 25, page: 1 });
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [total, setTotal] = useState(0);

  const params = useMemo(() => {
    const offset = (q.page - 1) * q.limit;
    const p = { ...q, offset };
    Object.keys(p).forEach(k => { if (p[k] === "" || p[k] === null) delete p[k]; });
    return p;
  }, [q]);

  function setSort(field, order){ setQ(prev => ({ ...prev, sort_by: field, sort_order: order, page: 1 })); run({ ...params, sort_by: field, sort_order: order, page: 1 }); }
  function onPageChange(p){ setQ(prev => ({ ...prev, page: p })); run({ ...params, page: p }); }

  function onSelectSuggestion(item){ setQ(prev => ({ ...prev, search: item.ticker })); run({ ...params, search: item.ticker, page: 1 }); }

  async function run(useParams){
    const callParams = useParams || params;
    // Inline validations
    if (callParams.min_price && callParams.max_price && Number(callParams.min_price) > Number(callParams.max_price)){
      toast.error("Min price cannot exceed Max price"); return;
    }
    if (callParams.limit > 1000){ toast.error("Limit cannot exceed 1000"); return; }

    setLoading(true); setError("");
    try {
      const r = await getStocks(callParams);
      const data = r.data || {};
      const list = data.data || data.stocks || [];
      setRows(list);
      setTotal(data.total_available || data.total_count || list.length);
    } catch (e){ setError("Failed to fetch stocks"); }
    finally { setLoading(false); }
  }

  return (
    <Layout>
      <PageHeader title="Stock Scanner" subtitle="Filter and search stocks with advanced criteria." />
      <Section>
        <div className="card p-6">
          <div className="grid md:grid-cols-3 gap-4">
            <AutosuggestSearch value={q.search} onChange={(v)=> setQ({...q, search:v})} onSelect={onSelectSuggestion} />
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
            <button className="btn btn-primary py-2" onClick={()=> run()} disabled={loading}>{loading? 'Running…' : 'Run'}</button>
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
                  <th className="py-2"><SortHeader label="Ticker" field="ticker" activeField={q.sort_by} order={q.sort_order} onChange={setSort} /></th>
                  <th className="py-2">Company</th>
                  <th className="py-2"><SortHeader label="Price" field="price" activeField={q.sort_by} order={q.sort_order} onChange={setSort} /></th>
                  <th className="py-2"><SortHeader label="Change%" field="change_percent" activeField={q.sort_by} order={q.sort_order} onChange={setSort} /></th>
                  <th className="py-2"><SortHeader label="Volume" field="volume" activeField={q.sort_by} order={q.sort_order} onChange={setSort} /></th>
                  <th className="py-2"><SortHeader label="Market Cap" field="market_cap" activeField={q.sort_by} order={q.sort_order} onChange={setSort} /></th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="6" className="py-6"><TableSkeleton rows={6} cols={6} /></td></tr>
                ) : rows.length === 0 ? (
                  <tr><td colSpan="6" className="py-6 text-center text-muted-foreground">No results</td></tr>
                ) : rows.map(s => (
                  <tr key={s.ticker || s.symbol} className="border-b border-border/70">
                    <td className="py-2 font-medium">{s.ticker || s.symbol}</td>
                    <td className="py-2 flex items-center gap-2">{s.company_name || s.name} {s.trend && <Badge color={s.trend === 'up' ? 'green' : s.trend === 'down' ? 'red' : 'neutral'}>{s.trend}</Badge>}</td>
                    <td className="py-2">{s.current_price}</td>
                    <td className={`py-2 ${s.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>{s.change_percent}</td>
                    <td className="py-2">{s.volume?.toLocaleString?.()}</td>
                    <td className="py-2">{s.market_cap?.toLocaleString?.()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={q.page} pageSize={q.limit} total={total} onChange={onPageChange} />
        </div>
      </Section>
    </Layout>
  );
}