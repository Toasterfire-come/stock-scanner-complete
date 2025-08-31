import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getWatchlist, addWatchlistItem, deleteWatchlistItem } from "../../lib/api";
import { Toaster, toast } from "sonner";

export default function Watchlists(){
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ symbol:"", watchlist_name:"My Watchlist", notes:"", alert_price:"" });

  const load = () => { getWatchlist().then(r=> setItems(r.data?.data || [])).catch(()=> setItems([])); };
  useEffect(()=>{ load(); },[]);

  const onSubmit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const payload = { ...form, alert_price: form.alert_price ? Number(form.alert_price) : null };
      await addWatchlistItem(payload);
      toast.success("Added to watchlist");
      setForm({ symbol:"", watchlist_name:"My Watchlist", notes:"", alert_price:"" });
      load();
    } catch { toast.error("Failed to add"); }
    finally { setLoading(false); }
  };

  return (
    <Layout>
      <Toaster richColors />
      <PageHeader title="Watchlists" subtitle="Track symbols with notes and target alerts." />
      <Section>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Add to watchlist</h3>
            <form onSubmit={onSubmit} className="space-y-4">
              <div><label className="label">Symbol</label><input className="input" value={form.symbol} onChange={(e)=> setForm({...form, symbol:e.target.value.toUpperCase()})} required /></div>
              <div><label className="label">Watchlist name</label><input className="input" value={form.watchlist_name} onChange={(e)=> setForm({...form, watchlist_name:e.target.value})} /></div>
              <div><label className="label">Notes</label><textarea className="input min-h-[100px]" value={form.notes} onChange={(e)=> setForm({...form, notes:e.target.value})} /></div>
              <div><label className="label">Alert price (optional)</label><input className="input" type="number" step="0.01" value={form.alert_price} onChange={(e)=> setForm({...form, alert_price:e.target.value})} /></div>
              <button className="btn btn-primary px-4 py-2" disabled={loading}>{loading? 'Adding…' : 'Add'}</button>
            </form>
          </div>
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Items</h3>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-2">Symbol</th>
                    <th className="py-2">Notes</th>
                    <th className="py-2">Alert Price</th>
                    <th className="py-2">Added</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {items.length === 0 ? <tr><td colSpan="5" className="py-6 text-center text-muted-foreground">No items</td></tr> : items.map(w => (
                    <tr key={w.id} className="border-b border-border/70">
                      <td className="py-2 font-medium">{w.symbol}</td>
                      <td className="py-2">{w.notes || '-'}</td>
                      <td className="py-2">{w.alert_price ?? '-'}</td>
                      <td className="py-2">{new Date(w.added_date).toLocaleString?.() || '-'}</td>
                      <td className="py-2 text-right"><button className="btn btn-outline px-2 py-1" onClick={async ()=>{ try { await deleteWatchlistItem(w.id); load(); } catch { toast.error('Delete failed'); } }}>Delete</button></td>
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