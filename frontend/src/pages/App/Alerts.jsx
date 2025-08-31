import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { getAllowedAlertSchema, createAlert, listAlerts } from "../../lib/api";
import { Toaster, toast } from "sonner";

export default function AlertsPage(){
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState({ ticker: "", target_price: "", condition: "above", email: "" });

  useEffect(()=>{
    getAllowedAlertSchema().then(r=> setSchema(r.data)).catch(()=>{});
    refreshList();
  },[]);

  function refreshList(){
    listAlerts({ limit: 20, active: true }).then(r=> setAlerts(r.data?.data || [])).catch(()=> setAlerts([]));
  }

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form, target_price: Number(form.target_price) };
      await createAlert(payload);
      toast.success("Alert created successfully");
      setForm({ ticker: "", target_price: "", condition: "above", email: "" });
      refreshList();
    } catch (err){
      toast.error("Failed to create alert. Please check inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Toaster richColors />
      <PageHeader title="Price Alerts" subtitle="Create price-based alerts and monitor active rules." cta={null} />
      <Section>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Create alert</h3>
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <label className="label">Ticker</label>
                <input className="input" placeholder="e.g., AAPL" value={form.ticker} onChange={(e)=> setForm({...form, ticker:e.target.value.toUpperCase()})} required />
              </div>
              <div>
                <label className="label">Target price</label>
                <input className="input" type="number" step="0.01" placeholder="e.g., 200" value={form.target_price} onChange={(e)=> setForm({...form, target_price:e.target.value})} required />
              </div>
              <div>
                <label className="label">Condition</label>
                <select className="input" value={form.condition} onChange={(e)=> setForm({...form, condition:e.target.value})}>
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                </select>
              </div>
              <div>
                <label className="label">Email</label>
                <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={(e)=> setForm({...form, email:e.target.value})} required />
              </div>
              <button disabled={loading} className="btn btn-primary px-4 py-2" type="submit">{loading ? 'Creating…' : 'Create alert'}</button>
              {schema && (
                <p className="text-xs text-muted-foreground">Endpoint: {schema.endpoint} • Method: {schema.method}</p>
              )}
            </form>
          </div>
          <div className="card p-6">
            <h3 className="font-semibold text-lg mb-4">Active alerts</h3>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-2">Ticker</th>
                    <th className="py-2">Type</th>
                    <th className="py-2">Target</th>
                    <th className="py-2">Created</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.length === 0 ? (
                    <tr><td colSpan="5" className="py-6 text-center text-muted-foreground">No alerts yet</td></tr>
                  ) : alerts.map(a => (
                    <tr key={a.id} className="border-b border-border/70">
                      <td className="py-2 font-medium">{a.ticker}</td>
                      <td className="py-2 capitalize">{a.alert_type}</td>
                      <td className="py-2">{a.target_value}</td>
                      <td className="py-2">{new Date(a.created_at).toLocaleString()}</td>
                      <td className="py-2">{a.is_active ? 'Active' : 'Inactive'}</td>
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