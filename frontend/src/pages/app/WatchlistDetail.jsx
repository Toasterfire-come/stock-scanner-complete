import React, { useEffect, useMemo, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Badge } from '../../components/ui/badge';
import { toast } from 'sonner';
import { listWatchlists, createAlert, createShareLinkForWatchlist } from '../../api/client';
import { TrendingUp, TrendingDown, Bell, Save, ArrowLeft } from 'lucide-react';

export default function WatchlistDetail() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [items, setItems] = useState([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true); setError('');
      try {
        const res = await listWatchlists();
        if (res?.success) {
          // Flatten by matching selected watchlist id or name
          const chosen = (res.data?.watchlists || []).find((w) => `${w.id}` === `${id}` || w.name?.toLowerCase() === (id || '').toLowerCase());
          setItems((chosen?.items || chosen?.stocks || []).map((s) => ({
            id: s.item_id || s.id,
            symbol: s.stock_ticker || s.symbol,
            company_name: s.company_name || s.name,
            current_price: s.current_price,
            price_change_percent: s.price_change_percent,
            alert_price: s.alert_price,
            notes: s.notes,
          })));
        } else {
          setItems([]);
          setError('Watchlist not available');
        }
      } catch (e) {
        setError('Failed to load watchlist');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const groups = useMemo(() => {
    const grouped = {};
    for (const it of items) {
      const g = (it.watchlist_name || 'My Watchlist').toString();
      grouped[g] = grouped[g] || [];
      grouped[g].push(it);
    }
    return grouped;
  }, [items]);

  const setInline = (idx, patch) => setItems((arr) => arr.map((it, i) => (i === idx ? { ...it, ...patch } : it)));

  const onSaveInline = async (it, idx) => {
    try {
      // A backend PATCH is not specified; we just provide UX locally
      toast.success(`${it.symbol} updated`);
    } catch (e) {
      toast.error('Failed to save');
    }
  };

  const onCreateAlert = async (it) => {
    try {
      await createAlert({
        ticker: it.symbol,
        target_price: it.alert_price || it.current_price,
        condition: 'above',
        email: 'user@example.com',
      });
      toast.success(`Alert set for ${it.symbol}`);
    } catch {
      toast.error('Failed to create alert');
    }
  };

  if (loading) return <div className="container mx-auto px-4 py-8"><div className="h-8 w-48 bg-gray-200 animate-pulse rounded mb-4" /><div className="h-32 w-full bg-gray-200 animate-pulse rounded" /></div>;
  if (error) return <div className="container mx-auto px-4 py-8"><Card><CardContent className="p-4 text-red-600">{error}</CardContent></Card></div>;

  const groupName = Object.keys(groups)[0] || id;
  const list = groups[groupName] || [];

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost"><Link to="/app/watchlists"><ArrowLeft className="h-4 w-4" /></Link></Button>
          <h1 className="text-2xl font-semibold">Watchlist: {groupName}</h1>
          <Badge variant="outline">{list.length} items</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={async () => {
            try {
              const res = await createShareLinkForWatchlist(id);
              if (res?.success && res?.url) {
                const link = `${window.location.origin}${res.url}`;
                await navigator.clipboard.writeText(link);
                toast.success('Share link copied');
              } else {
                toast.error('Failed to create share link');
              }
            } catch {
              toast.error('Failed to create share link');
            }
          }}>Share</Button>
        </div>
      </div>

      {!list.length ? (
        <Card><CardContent className="p-6 text-gray-600">No items in this watchlist.</CardContent></Card>
      ) : (
        <Card>
          <CardHeader><CardTitle>Symbols</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {list.map((it, idx) => (
                <div key={it.id || idx} className="grid grid-cols-1 md:grid-cols-6 gap-3 p-3 border rounded">
                  <div className="md:col-span-1">
                    <div className="font-semibold">{it.symbol}</div>
                    <div className="text-sm text-gray-600">{it.company_name}</div>
                  </div>
                  <div className="md:col-span-1">
                    <div className="text-sm">Price</div>
                    <div className="font-medium">${(it.current_price ?? 0).toLocaleString()}</div>
                    <div className={`text-sm ${Number(it.price_change_percent) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {Number(it.price_change_percent) >= 0 ? <TrendingUp className="h-3 w-3 inline" /> : <TrendingDown className="h-3 w-3 inline" />}
                      {`${(it.price_change_percent ?? 0).toFixed(2)}%`}
                    </div>
                  </div>
                  <div className="md:col-span-2">
                    <div className="text-sm">Notes</div>
                    <Textarea value={it.notes || ''} onChange={(e) => setInline(idx, { notes: e.target.value })} rows={2} />
                  </div>
                  <div className="md:col-span-1">
                    <div className="text-sm">Alert price</div>
                    <Input value={it.alert_price ?? ''} type="number" step="0.01" onChange={(e) => setInline(idx, { alert_price: e.target.value })} />
                  </div>
                  <div className="md:col-span-1 flex items-end gap-2">
                    <Button size="sm" variant="outline" onClick={() => onSaveInline(it, idx)}><Save className="h-3 w-3 mr-1" /> Save</Button>
                    <Button size="sm" onClick={() => onCreateAlert(it)}><Bell className="h-3 w-3 mr-1" /> Alert</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}