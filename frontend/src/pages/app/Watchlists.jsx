import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../../components/ui/dialog";
import { toast } from "sonner";
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  Star,
  Trash2,
  Eye,
  Bell,
  Search
} from "lucide-react";
import { getWatchlist, addWatchlist, deleteWatchlist } from "../../api/client";
import { useAuth } from "../../context/SecureAuthContext";

const Watchlists = () => {
  const { isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [watchlist, setWatchlist] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [newWatchItem, setNewWatchItem] = useState({
    symbol: "",
    notes: "",
    alert_price: "",
    watchlist_name: "My Watchlist"
  });

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const response = await getWatchlist();
      if (response && response.success) {
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

  const handleAddToWatchlist = async (e) => {
    e.preventDefault();
    if (!newWatchItem.symbol) {
      toast.error("Please enter a stock symbol");
      return;
    }

    try {
      const payload = {
        symbol: newWatchItem.symbol.toUpperCase(),
        watchlist_name: newWatchItem.watchlist_name,
        notes: newWatchItem.notes,
        alert_price: newWatchItem.alert_price ? parseFloat(newWatchItem.alert_price) : null
      };

      const response = await addWatchlist(payload.symbol, payload);

      if (response.success) {
        toast.success(`${newWatchItem.symbol.toUpperCase()} added to watchlist`);
        setNewWatchItem({ symbol: "", notes: "", alert_price: "", watchlist_name: "My Watchlist" });
        setIsAddModalOpen(false);
        fetchWatchlist();
      } else {
        toast.error(response.message || "Failed to add to watchlist");
      }
    } catch (error) {
      toast.error("Failed to add stock to watchlist");
    }
  };

  const handleRemoveFromWatchlist = async (id, symbol) => {
    if (!confirm(`Are you sure you want to remove ${symbol} from your watchlist?`)) return;
    
    try {
      const response = await deleteWatchlist(id);
      if (response.success) {
        toast.success(`${symbol} removed from watchlist`);
        fetchWatchlist();
      } else {
        toast.error("Failed to remove from watchlist");
      }
    } catch (error) {
      toast.error("Failed to remove from watchlist");
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatVolume = (v) => {
    const n = Number(v || 0);
    if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
    return n.toLocaleString();
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const filteredWatchlist = watchlist?.data?.filter(item =>
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.company_name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Card>
          <CardHeader>
            <CardTitle>Watchlists</CardTitle>
            <CardDescription>Sign in to create and manage your watchlists</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-gray-600">You need to be signed in to view your saved watchlist items.</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Graceful message if empty and not authenticated will be handled by add form disabled state in future

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Watchlists</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Keep track of stocks you're interested in</p>
          </div>
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Stock
              </Button>
            </DialogTrigger>
            <DialogContent aria-describedby="watchlist-dialog-desc">
              <DialogTitle className="sr-only">Create Watchlist</DialogTitle>
              <DialogDescription id="watchlist-dialog-desc" className="sr-only">Create or edit your watchlist</DialogDescription>
              <DialogHeader>
                <DialogTitle>Add Stock to Watchlist</DialogTitle>
                <DialogDescription>
                  Add a stock to your watchlist to monitor its performance
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddToWatchlist} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="symbol">Stock Symbol</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g. AAPL"
                    value={newWatchItem.symbol}
                    onChange={(e) => setNewWatchItem({...newWatchItem, symbol: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notes">Notes (Optional)</Label>
                  <Input
                    id="notes"
                    placeholder="Why are you watching this stock?"
                    value={newWatchItem.notes}
                    onChange={(e) => setNewWatchItem({...newWatchItem, notes: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="alert_price">Price Alert (Optional)</Label>
                  <Input
                    id="alert_price"
                    type="number"
                    step="0.01"
                    placeholder="e.g. 150.00"
                    value={newWatchItem.alert_price}
                    onChange={(e) => setNewWatchItem({...newWatchItem, alert_price: e.target.value})}
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">Add to Watchlist</Button>
                  <Button type="button" variant="outline" onClick={() => setIsAddModalOpen(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary Cards */}
        {watchlist?.summary && (
          <div className="grid md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</p>
                    <p className="text-2xl font-bold">{watchlist.summary.total_items}</p>
                  </div>
                  <Star className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Gainers</p>
                    <div className="flex items-center">
                      <p className="text-2xl font-bold text-green-600">{watchlist.summary.gainers}</p>
                      <TrendingUp className="h-5 w-5 text-green-500 ml-2" />
                    </div>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Losers</p>
                    <div className="flex items-center">
                      <p className="text-2xl font-bold text-red-600">{watchlist.summary.losers}</p>
                      <TrendingDown className="h-5 w-5 text-red-500 ml-2" />
                    </div>
                  </div>
                  <TrendingDown className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">With Alerts</p>
                    <p className="text-2xl font-bold">{watchlist.data?.filter(item => item.alert_price).length || 0}</p>
                  </div>
                  <Bell className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Search */}
        <Card>
          <CardContent className="p-6">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400 dark:text-gray-500" />
              <Input 
                placeholder="Search watchlist..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10" 
              />
            </div>
          </CardContent>
        </Card>

        {/* Watchlist Items */}
        <Card>
          <CardHeader>
            <CardTitle>Your Watchlist</CardTitle>
            <CardDescription>
              Stocks you're monitoring - {filteredWatchlist.length} items
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredWatchlist.length > 0 ? (
              <div className="space-y-4">
                {/* Desktop Table */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50 dark:bg-gray-800/60">
                        <th className="text-left p-4 font-medium">Symbol</th>
                        <th className="text-left p-4 font-medium">Company</th>
                        <th className="text-right p-4 font-medium">Price</th>
                        <th className="text-right p-4 font-medium">Change</th>
                        <th className="text-right p-4 font-medium">% Change</th>
                        <th className="text-right p-4 font-medium">Volume</th>
                        <th className="text-left p-4 font-medium">Notes</th>
                        <th className="text-center p-4 font-medium">Alert</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredWatchlist.map((item) => (
                        <tr key={item.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="p-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <span className="font-bold text-blue-600 text-sm">{item.symbol.substring(0, 2)}</span>
                              </div>
                              <div>
                                <Link to={`/app/stocks/${item.symbol}`} className="font-semibold text-blue-600 hover:underline">
                                  {item.symbol}
                                </Link>
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="font-medium text-gray-900 dark:text-gray-100">{item.company_name}</div>
                          </td>
                          <td className="p-4 text-right font-medium">{formatCurrency(item.current_price)}</td>
                          <td className={`p-4 text-right ${item.price_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {item.price_change >= 0 ? '+' : ''}{item.price_change?.toFixed(2)}
                          </td>
                          <td className={`p-4 text-right font-medium ${item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            <div className="flex items-center justify-end">
                              {item.price_change_percent >= 0 ? 
                                <TrendingUp className="h-3 w-3 mr-1" /> : 
                                <TrendingDown className="h-3 w-3 mr-1" />
                              }
                              {formatPercentage(item.price_change_percent)}
                            </div>
                          </td>
                          <td className="p-4 text-right text-gray-600 dark:text-gray-400">{formatVolume(item.volume)}</td>
                          <td className="p-4">
                            <div className="text-sm text-gray-600 dark:text-gray-400 max-w-32 truncate" title={item.notes}>
                              {item.notes || '-'}
                            </div>
                          </td>
                          <td className="p-4 text-center">
                            {item.alert_price ? (
                              <Badge variant="secondary" className="text-xs">
                                <Bell className="h-3 w-3 mr-1" />
                                {formatCurrency(item.alert_price)}
                              </Badge>
                            ) : (
                              <span className="text-gray-400 dark:text-gray-500">-</span>
                            )}
                          </td>
                          <td className="p-4">
                            <div className="flex items-center justify-center space-x-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                asChild
                                title="View Details"
                              >
                                <Link to={`/app/stocks/${item.symbol}`}>
                                  <Eye className="h-4 w-4" />
                                </Link>
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => handleRemoveFromWatchlist(item.id, item.symbol)}
                                className="text-red-600 hover:text-red-700"
                                title="Remove from Watchlist"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Cards */}
                <div className="lg:hidden space-y-4">
                  {filteredWatchlist.map((item) => (
                    <Card key={item.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                              <span className="font-bold text-blue-600">{item.symbol.substring(0, 2)}</span>
                            </div>
                            <div>
                              <Link to={`/app/stocks/${item.symbol}`} className="font-semibold text-blue-600 hover:underline">
                                {item.symbol}
                              </Link>
                              <div className="text-sm text-gray-600">{item.company_name}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-lg">{formatCurrency(item.current_price)}</div>
                            <div className={`text-sm font-medium ${item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'} flex items-center justify-end`}>
                              {item.price_change_percent >= 0 ? 
                                <TrendingUp className="h-3 w-3 mr-1" /> : 
                                <TrendingDown className="h-3 w-3 mr-1" />
                              }
                              {formatPercentage(item.price_change_percent)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          {item.notes && (
                            <div className="text-sm">
                              <span className="text-gray-500">Notes: </span>
                              <span className="text-gray-700">{item.notes}</span>
                            </div>
                          )}
                          {item.alert_price && (
                            <div className="text-sm">
                              <Badge variant="secondary" className="text-xs">
                                <Bell className="h-3 w-3 mr-1" />
                                Alert at {formatCurrency(item.alert_price)}
                              </Badge>
                            </div>
                          )}
                          <div className="flex items-center justify-between pt-2">
                            <div className="text-sm text-gray-600">Vol: {formatVolume(item.volume)}</div>
                            <div className="flex space-x-2">
                              <Button size="sm" variant="ghost" asChild>
                                <Link to={`/app/stocks/${item.symbol}`}>
                                  <Eye className="h-4 w-4" />
                                </Link>
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => handleRemoveFromWatchlist(item.id, item.symbol)}
                                className="text-red-600"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Star className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {searchTerm ? "No matching stocks found" : "Your watchlist is empty"}
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm 
                    ? `No stocks match "${searchTerm}". Try a different search term.`
                    : "Add stocks to your watchlist to keep track of their performance"
                  }
                </p>
                {!searchTerm && (
                  <Button onClick={() => setIsAddModalOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Stock
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Watchlists;