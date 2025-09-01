import React, { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Textarea } from "../../components/ui/textarea";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../../components/ui/dialog";
import { toast } from "sonner";
import { Plus, Star, TrendingUp, TrendingDown, Trash2, Edit, Bell, Eye, RefreshCw, Search, Filter } from "lucide-react";
import { getWatchlist, addWatchlist, deleteWatchlist, createAlert } from "../../api/client";
import VirtualizedList from "../../components/VirtualizedList";

const Watchlists = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [watchlist, setWatchlist] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("added_date");
  const [newStock, setNewStock] = useState({ symbol: "", watchlist_name: "My Watchlist", notes: "", alert_price: "" });
  const [page, setPage] = useState(1);
  const pageSize = 30;

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const response = await getWatchlist();
        if (response.success) {
          setWatchlist(response);
        } else {
          setWatchlist({ success: true, data: [], summary: { total_items: 0, gainers: 0, losers: 0, unchanged: 0 } });
        }
      } catch (error) {
        toast.error("Failed to load watchlist");
      } finally {
        setIsLoading(false);
      }
    };
    fetchWatchlist();
  }, []);

  const handleAddStock = async (e) => {
    e.preventDefault(); setIsAdding(true);
    try {
      const response = await addWatchlist(newStock.symbol.toUpperCase(), { watchlist_name: newStock.watchlist_name, notes: newStock.notes, alert_price: newStock.alert_price ? parseFloat(newStock.alert_price) : null });
      if (response.success) {
        toast.success(`${newStock.symbol.toUpperCase()} added to watchlist`);
        setIsAddModalOpen(false);
        setNewStock({ symbol: "", watchlist_name: "My Watchlist", notes: "", alert_price: "" });
        const updated = await getWatchlist(); if (updated.success) setWatchlist(updated);
      } else { toast.error("Failed to add stock to watchlist"); }
    } catch { toast.error("Failed to add stock to watchlist"); } finally { setIsAdding(false); }
  };

  const handleRemoveStock = async (id, symbol) => {
    try {
      const response = await deleteWatchlist(id);
      if (response.success) {
        toast.success(`${symbol} removed from watchlist`);
        setWatchlist(prev => ({ ...prev, data: prev.data.filter(item => item.id !== id), summary: { ...prev.summary, total_items: Math.max(0, (prev.summary?.total_items || 1) - 1) } }));
      } else { toast.error("Failed to remove stock"); }
    } catch { toast.error("Failed to remove stock"); }
  };

  const handleCreateAlert = async (symbol, currentPrice) => {
    try {
      await createAlert({ ticker: symbol, target_price: currentPrice * 1.05, condition: "above", email: "user@example.com" });
      toast.success(`Price alert created for ${symbol}`);
    } catch { toast.error(`Failed to create alert for ${symbol}`); }
  };

  const filtered = useMemo(() => (watchlist?.data || []).filter(item => (item.symbol || '').toLowerCase().includes(searchTerm.toLowerCase()) || (item.company_name || '').toLowerCase().includes(searchTerm.toLowerCase()) || (item.notes || '').toLowerCase().includes(searchTerm.toLowerCase())), [watchlist, searchTerm]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    switch (sortBy) {
      case "symbol": return arr.sort((a,b) => (a.symbol || '').localeCompare(b.symbol || ''));
      case "price": return arr.sort((a,b) => (b.current_price || 0) - (a.current_price || 0));
      case "change": return arr.sort((a,b) => (b.price_change_percent || 0) - (a.price_change_percent || 0));
      case "added_date": return arr.sort((a,b) => new Date(b.added_date || 0) - new Date(a.added_date || 0));
      default: return arr;
    }
  }, [filtered, sortBy]);

  const total = sorted.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const pageSlice = sorted.slice((page - 1) * pageSize, page * pageSize);
  const useVirtual = total > 300;

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl"><div className="space-y-6"><div className="flex items-center justify-between"><Skeleton className="h-8 w-48" /><Skeleton className="h-10 w-32" /></div><div className="grid md:grid-cols-4 gap-6">{[1,2,3,4].map(i => <Card key={i}><CardContent className="p-6"><Skeleton className="h-8 w-16 mb-2" /><Skeleton className="h-4 w-24" /></CardContent></Card>)}</div><Card><CardHeader><Skeleton className="h-6 w-32" /></CardHeader><CardContent><div className="space-y-4">{[1,2,3,4].map(i => <div key={i} className="flex items-center justify-between p-4 border rounded"><Skeleton className="h-4 w-32" /><Skeleton className="h-4 w-16" /></div>)}</div></CardContent></Card></div></div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Watchlists</h1>
            <p className="text-gray-600 mt-2">Monitor stocks you're interested in</p>
          </div>
          <div className="flex items-center gap-2">
            <Input placeholder="Search symbols, names or notes..." value={searchTerm} onChange={(e)=>{ setPage(1); setSearchTerm(e.target.value); }} className="w-64" />
            <Button onClick={() => setPage(1)} variant="outline"><Search className="h-4 w-4 mr-1" />Filter</Button>
          </div>
        </div>

        {/* Summary */}
        {watchlist?.summary && (
          <div className="grid md:grid-cols-4 gap-6">
            <Card><CardContent className="p-6"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Total Stocks</p><p className="text-2xl font-bold">{watchlist.summary.total_items}</p></div><Star className="h-8 w-8 text-blue-500" /></div></CardContent></Card>
            <Card><CardContent className="p-6"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Gainers</p><p className="text-2xl font-bold text-green-600">{watchlist.summary.gainers}</p></div><TrendingUp className="h-8 w-8 text-green-500" /></div></CardContent></Card>
            <Card><CardContent className="p-6"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Losers</p><p className="text-2xl font-bold text-red-600">{watchlist.summary.losers}</p></div><TrendingDown className="h-8 w-8 text-red-500" /></div></CardContent></Card>
            <Card><CardContent className="p-6"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Unchanged</p><p className="text-2xl font-bold">{watchlist.summary.unchanged}</p></div><RefreshCw className="h-8 w-8 text-gray-500" /></div></CardContent></Card>
          </div>
        )}

        {/* List */}
        <Card>
          <CardHeader><CardTitle>All Items</CardTitle><CardDescription>Filtered list • {total} items</CardDescription></CardHeader>
          <CardContent>
            {total === 0 ? (
              <div className="text-center text-gray-600 py-12">No items. Add your first stock to the watchlist.</div>
            ) : (
              <>
                {/* Desktop virtualized when large */}
                <div className="hidden lg:block">
                  <div className="grid grid-cols-7 font-medium text-sm text-muted-foreground pb-2 border-b">
                    <div>Symbol</div><div>Company</div><div className="text-right">Price</div><div className="text-right">Change</div><div className="text-right">Volume</div><div className="text-right">Market Cap</div><div className="text-center">Actions</div>
                  </div>
                  {useVirtual ? (
                    <div className="border rounded mt-2">
                      <VirtualizedList
                        items={pageSlice}
                        itemSize={64}
                        height={600}
                        row={({ index, style, item }) => (
                          <div key={item.id || index} style={{...style, display:'grid', gridTemplateColumns:'1.5fr 3fr 1fr 1fr 1fr 1fr 1fr', alignItems:'center'}} className="border-b px-3">
                            <div className="font-semibold">{item.symbol}</div>
                            <div className="truncate">{item.company_name}</div>
                            <div className="text-right font-medium">${(item.current_price ?? 0).toLocaleString()}</div>
                            <div className={`text-right ${Number(item.price_change_percent)>=0?'text-green-600':'text-red-600'}`}>{Number(item.price_change_percent||0).toFixed(2)}%</div>
                            <div className="text-right text-muted-foreground">{(item.volume ?? 0).toLocaleString()}</div>
                            <div className="text-right text-muted-foreground">${((item.market_cap ?? 0)/1e9).toFixed(1)}B</div>
                            <div className="text-center flex items-center justify-center gap-2 py-2">
                              <Button size="sm" variant="outline" asChild><Link to={`/app/stocks/${item.symbol}`}>View</Link></Button>
                              <Button size="sm" variant="outline" onClick={() => handleCreateAlert(item.symbol, item.current_price)}><Bell className="h-4 w-4" /></Button>
                              <Button size="sm" variant="destructive" onClick={() => handleRemoveStock(item.id, item.symbol)}><Trash2 className="h-4 w-4" /></Button>
                            </div>
                          </div>
                        )}
                      />
                    </div>
                  ) : (
                    <div className="space-y-2 mt-2">
                      {pageSlice.map((item) => (
                        <div key={item.id} className="grid grid-cols-7 items-center border rounded px-3 py-3">
                          <div className="font-semibold">{item.symbol}</div>
                          <div className="truncate">{item.company_name}</div>
                          <div className="text-right font-medium">${(item.current_price ?? 0).toLocaleString()}</div>
                          <div className={`text-right ${Number(item.price_change_percent)>=0?'text-green-600':'text-red-600'}`}>{Number(item.price_change_percent||0).toFixed(2)}%</div>
                          <div className="text-right text-muted-foreground">{(item.volume ?? 0).toLocaleString()}</div>
                          <div className="text-right text-muted-foreground">${((item.market_cap ?? 0)/1e9).toFixed(1)}B</div>
                          <div className="text-center flex items-center justify-center gap-2">
                            <Button size="sm" variant="outline" asChild><Link to={`/app/stocks/${item.symbol}`}>View</Link></Button>
                            <Button size="sm" variant="outline" onClick={() => handleCreateAlert(item.symbol, item.current_price)}><Bell className="h-4 w-4" /></Button>
                            <Button size="sm" variant="destructive" onClick={() => handleRemoveStock(item.id, item.symbol)}><Trash2 className="h-4 w-4" /></Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Mobile cards */}
                <div className="lg:hidden space-y-3">
                  {pageSlice.map((item) => (
                    <Card key={item.id}><CardContent className="p-4"><div className="flex items-center justify-between"><div><div className="font-semibold">{item.symbol}</div><div className="text-muted-foreground text-sm">{item.company_name}</div></div><div className="text-right"><div className="font-semibold">${(item.current_price ?? 0).toLocaleString()}</div><div className={`${Number(item.price_change_percent)>=0?'text-green-600':'text-red-600'} text-sm`}>{Number(item.price_change_percent||0).toFixed(2)}%</div></div></div><div className="flex items-center justify-end gap-2 mt-3"><Button size="sm" asChild variant="outline"><Link to={`/app/stocks/${item.symbol}`}>View</Link></Button><Button size="sm" variant="outline" onClick={() => handleCreateAlert(item.symbol, item.current_price)}>Alert</Button><Button size="sm" variant="destructive" onClick={() => handleRemoveStock(item.id, item.symbol)}>Remove</Button></div></CardContent></Card>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6">
                    <div className="text-sm text-muted-foreground">Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total.toLocaleString()} items</div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page===1}>Previous</Button>
                      <div className="flex gap-1">{Array.from({ length: Math.min(totalPages, 5) }, (_, i) => { const p = Math.max(1, page - 2) + i; if (p > totalPages) return null; return (<Button key={p} variant={p===page?"default":"outline"} size="sm" onClick={()=>setPage(p)}>{p}</Button>); })}</div>
                      <Button variant="outline" size="sm" onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page===totalPages}>Next</Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Add Modal */}
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Add Stock</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add Stock to Watchlist</DialogTitle><DialogDescription>Add a stock to monitor its price and performance</DialogDescription></DialogHeader>
            <form onSubmit={handleAddStock} className="space-y-4">
              <div className="space-y-2"><Label htmlFor="symbol">Stock Symbol</Label><Input id="symbol" placeholder="e.g., AAPL" value={newStock.symbol} onChange={(e)=>setNewStock(prev=>({...prev, symbol:e.target.value}))} required /></div>
              <div className="space-y-2"><Label htmlFor="watchlist_name">Watchlist Name</Label><Input id="watchlist_name" placeholder="My Watchlist" value={newStock.watchlist_name} onChange={(e)=>setNewStock(prev=>({...prev, watchlist_name:e.target.value}))} /></div>
              <div className="space-y-2"><Label htmlFor="notes">Notes (Optional)</Label><Textarea id="notes" placeholder="Add notes about this stock..." rows={3} value={newStock.notes} onChange={(e)=>setNewStock(prev=>({...prev, notes:e.target.value}))} /></div>
              <div className="space-y-2"><Label htmlFor="alert_price">Alert Price (Optional)</Label><Input id="alert_price" type="number" step="0.01" placeholder="0.00" value={newStock.alert_price} onChange={(e)=>setNewStock(prev=>({...prev, alert_price:e.target.value}))} /></div>
              <div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={()=>setIsAddModalOpen(false)}>Cancel</Button><Button type="submit" disabled={isAdding}>{isAdding?"Adding...":"Add to Watchlist"}</Button></div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default Watchlists;