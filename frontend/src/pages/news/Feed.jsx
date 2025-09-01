import React, { useEffect, useState } from 'react';
import { endpoints } from '../../lib/api';
import { Bell, Newspaper, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export default function NewsFeed() {
  const [state, setState] = useState({ loading: true, error: '', items: [] });

  const load = async () => {
    setState(s => ({ ...s, loading: true, error: '' }));
    const res = await endpoints.news.feed({ limit: 20 });
    if (!res.ok) {
      setState({ loading: false, error: res.error || 'Failed to load', items: [] });
      toast.error(`News failed: ${res.error}`);
    } else {
      const items = res.data?.data?.news_items || res.data?.data || res.data?.news || [];
      setState({ loading: false, error: '', items });
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">News Feed</h1>
        <button onClick={load} className="inline-flex items-center gap-2 px-3 py-2 rounded-md border hover:bg-accent">
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {state.loading && <ListSkeleton />}
      {state.error && (
        <div className="p-4 border rounded bg-destructive/10 text-destructive">{state.error}</div>
      )}

      {!state.loading && !state.error && (
        <div className="space-y-3">
          {state.items.map((n) => (
            <article key={n.id} className="p-4 border rounded">
              <div className="text-sm text-muted-foreground">{n.source} • {formatDate(n.published_at)}</div>
              <h2 className="text-lg font-medium mt-1">{n.title}</h2>
              {n.summary && <p className="text-sm text-muted-foreground mt-1">{n.summary}</p>}
              <div className="mt-2 text-sm">
                <a href={n.url} target="_blank" rel="noreferrer" className="text-primary hover:underline">Read more</a>
              </div>
            </article>
          ))}
          {!state.items.length && (
            <div className="p-6 border rounded text-center text-muted-foreground">
              <Newspaper className="h-5 w-5 mx-auto mb-2" /> No news available
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-muted animate-pulse rounded" />)}
    </div>
  );
}

function formatDate(str) {
  if (!str) return '';
  try { return new Date(str).toLocaleString(); } catch { return str; }
}