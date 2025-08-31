import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getPortfolio, addHolding, deleteHolding } from "../../lib/api";
import { Toaster, toast } from "sonner";

export default function Portfolio(){
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ symbol:"", shares:"", avg_cost:"", portfolio_name:"My Portfolio" });

  const load = () => {
    getPortfolio().then(r=> setItems(r.data?.data || [])).catch(()=> setItems([]));
  };

  useEffect(()=>{ load(); },[]);

  const onSubmit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      await addHolding({ ...form, shares: Number(form.shares), avg_cost: Number(form.avg_cost) });
      toast.success("Holding added");
      setForm({ symbol:"", shares:"", avg_cost:"", portfolio_name:"My Portfolio" });
      load();
    } catch {
      toast.error("Failed to add");
    } finally { setLoading(false); }
  };

  return (
    <Layout>
      <Toaster richColors />
      <PageHeader title="Portfolio" subtitle="Track positions and performance." />
      <Section>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Add Holding</h3>
            <form onSubmit={onSubmit} className="space-y-4">
              <div><label className="label">Symbol</label><input className="input" value={form.symbol} onChange={(e)=> setForm({...form, symbol:e.target.value.toUpperCase()})} placeholder="e.g., AAPL" required /></div>
              <div><label className="label">Shares</label><input className="input" type="number" value={form.shares} onChange={(e)=> setForm({...form, shares:e.target.value})} required /></div>
              <div><label className="label">Average Cost</label><input className="input" type="number" step="0.01" value={form.avg_cost} onChange={(e)=> setForm({...form, avg_cost:e.target.value})} required /></div>
              <div><label className="label">Portfolio name</label><input className="input" value={form.portfolio_name} onChange={(e)=> setForm({...form, portfolio_name:e.target.value})} /></div>
              <button className="btn btn-primary px-4 py-2" disabled={loading}>{loading? 'Adding…':'Add'}</button>
            </form>
          </div>
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Holdings</h3>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-2">Symbol</th>
                    <th className="py-2">Shares</th>
                    <th className="py-2">Avg Cost</th>
                    <th className="py-2">Value</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {items.length === 0 ? <tr><td colSpan="5" className="py-6 text-center text-muted-foreground">No holdings</td></tr> : items.map(h => (
                    <tr key={h.id} className="border-b border-border/70">
                      <td className="py-2 font-medium">{h.symbol}</td>
                      <td className="py-2">{h.shares}</td>
                      <td className="py-2">{h.avg_cost}</td>
                      <td className="py-2">{h.total_value ?? '-'}</td>
                      <td className="py-2 text-right">
                        <button className="btn btn-outline px-2 py-1" onClick={async ()=>{ try{ await deleteHolding(h.id); load(); } catch { toast.error('Delete failed'); } }}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Section>
    </Layout>
  );
}