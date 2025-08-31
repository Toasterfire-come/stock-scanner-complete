import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import PageHeader from "../../components/PageHeader";
import Section from "../../components/Section";
import { api } from "../../lib/api";
import { TableSkeleton } from "../../components/Skeletons";
import { toast } from "sonner";

export default function Notifications(){
  const [items, setItems] = useState([]);
  const [meta, setMeta] = useState({ page: 1, limit: 20, total_unread: 0 });
  const [loading, setLoading] = useState(false);

  async function load(page = 1){
    setLoading(true);
    try {
      const r = await api.get(`/notifications/history/`, { params: { page, limit: meta.limit } });
      setItems(r.data?.data || []);
      setMeta({ ...meta, page, total_unread: r.data?.summary?.total_unread || 0 });
    } catch { toast.error("Failed to load notifications"); }
    finally { setLoading(false); }
  }

  async function markRead(id){
    try { await api.post(`/notifications/mark-read/`, { notification_ids: [id] }); load(meta.page); }
    catch { toast.error("Failed to mark read"); }
  }

  useEffect(()=>{ load(1); // initial load
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);

  return (
    <Layout>
      <PageHeader title="Notifications" subtitle={`Total unread: ${meta.total_unread}`} />
      <Section>
        <div className="card p-6">
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b border-border">
                  <th className="py-2">Title</th>
                  <th className="py-2">Type</th>
                  <th className="py-2">Created</th>
                  <th className="py-2">Read</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="5" className="py-6"><TableSkeleton rows={6} cols={5} /></td></tr>
                ) : items.length === 0 ? (
                  <tr><td colSpan="5" className="py-6 text-center text-muted-foreground">No notifications</td></tr>
                ) : items.map(n => (
                  <tr key={n.id} className="border-b border-border/70">
                    <td className="py-2 font-medium">{n.title}</td>
                    <td className="py-2">{n.type}</td>
                    <td className="py-2">{new Date(n.created_at).toLocaleString?.()}</td>
                    <td className="py-2">{n.is_read ? 'Yes' : 'No'}</td>
                    <td className="py-2 text-right"><button className="btn btn-outline px-2 py-1" onClick={()=> markRead(n.id)}>Mark read</button></td>
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