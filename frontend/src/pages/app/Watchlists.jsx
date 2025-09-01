import React, { useState, useEffect } from "react";
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
import { 
  Plus, 
  Star, 
  TrendingUp, 
  TrendingDown, 
  Trash2,
  Edit,
  Bell,
  Eye,
  RefreshCw,
  Search,
  Filter
} from "lucide-react";
import { getWatchlist, addWatchlist, deleteWatchlist, createAlert } from "../../api/client";

const Watchlists = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [watchlist, setWatchlist] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("added_date");
  const [newStock, setNewStock] = useState({
    symbol: "",
    watchlist_name: "My Watchlist",
    notes: "",
    alert_price: ""
  });

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const response = await getWatchlist();
        if (response.success) {
          setWatchlist(response);
        } else {
          // Mock watchlist data
          setWatchlist({
            success: true,
            data: [
              {
                id: "1",
                symbol: "AAPL",
                company_name: "Apple Inc.",
                current_price: 175.25,
                price_change: 2.34,
                price_change_percent: 1.35,
                volume: 52341234,
                market_cap: 2800000000000,
                watchlist_name: "My Watchlist",
                added_date: "2024-03-10T10:30:00Z",
                notes: "Waiting for earnings report",
                alert_price: 180.00
              },
              {
                id: "2",
                symbol: "TSLA",
                company_name: "Tesla, Inc.",
                current_price: 198.50,
                price_change: -5.75,
                price_change_percent: -2.81,
                volume: 89765432,
                market_cap: 630000000000,
                watchlist_name: "My Watchlist",
                added_date: "2024-03-08T14:20:00Z",
                notes: "High volatility stock",
                alert_price: 200.00
              },
              {
                id: "3",
                symbol: "NVDA",
                company_name: "NVIDIA Corporation",
                current_price: 875.43,
                price_change: 15.67,
                price_change_percent: 1.82,
                volume: 65432109,
                market_cap: 2200000000000,
                watchlist_name: "Tech Stocks",
                added_date: "2024-03-05T09:15:00Z",
                notes: "AI growth play",
                alert_price: 900.00
              },
              {
                id: "4",
                symbol: "AMD",
                company_name: "Advanced Micro Devices",
                current_price: 163.25,
                price_change: 3.80,
                price_change_percent: 2.38,
                volume: 34567890,
                market_cap: 264000000000,
                watchlist_name: "Tech Stocks",
                added_date: "2024-03-01T16:45:00Z",
                notes: "Competitor to NVDA",
                alert_price: null
              }
            ],
            summary: {
              total_items: 4,
              gainers: 3,
              losers: 1,
              unchanged: 0
            }
          });
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
    e.preventDefault();
    setIsAdding(true);

    try {
      const response = await addWatchlist(newStock.symbol.toUpperCase(), {
        watchlist_name: newStock.watchlist_name,
        notes: newStock.notes,
        alert_price: newStock.alert_price ? parseFloat(newStock.alert_price) : null
      });

      if (response.success) {
        toast.success(`${newStock.symbol.toUpperCase()} added to watchlist`);
        setIsAddModalOpen(false);
        setNewStock({ symbol: "", watchlist_name: "My Watchlist", notes: "", alert_price: "" });
        
        // Refresh watchlist data
        const updatedWatchlist = await getWatchlist();
        if (updatedWatchlist.success) {
          setWatchlist(updatedWatchlist);
        }
      } else {
        toast.error("Failed to add stock to watchlist");
      }
    } catch (error) {
      toast.error("Failed to add stock to watchlist");
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemoveStock = async (id, symbol) => {
    try {
      const response = await deleteWatchlist(id);
      if (response.success) {
        toast.success(`${symbol} removed from watchlist`);
        setWatchlist(prev => ({
          ...prev,
          data: prev.data.filter(item => item.id !== id),
          summary: {
            ...prev.summary,
            total_items: prev.summary.total_items - 1
          }
        }));
      } else {
        toast.error("Failed to remove stock");
      }
    } catch (error) {
      toast.error("Failed to remove stock");
    }
  };

  const handleCreateAlert = async (symbol, currentPrice) => {
    try {
      await createAlert({
        ticker: symbol,
        target_price: currentPrice * 1.05, // 5% above current
        condition: "above",
        email: "user@example.com" // Should come from user context
      });
      toast.success(`Price alert created for ${symbol}`);
    } catch (error) {
      toast.error(`Failed to create alert for ${symbol}`);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatMarketCap = (value) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value.toLocaleString()}`;
  };

  const formatVolume = (value) => {
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
    return value.toLocaleString();
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const filteredWatchlist = watchlist?.data?.filter(item =>
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.notes?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const sortedWatchlist = [...filteredWatchlist].sort((a, b) => {
    switch (sortBy) {
      case "symbol":
        return a.symbol.localeCompare(b.symbol);
      case "price":
        return b.current_price - a.current_price;
      case "change":
        return b.price_change_percent - a.price_change_percent;
      case "added_date":
        return new Date(b.added_date) - new Date(a.added_date);
      default:
        return 0;
    }
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
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

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Watchlists</h1>
            <p className="text-gray-600 mt-2">
              Monitor stocks you're interested in
            </p>
          </div>
          
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Stock
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Stock to Watchlist</DialogTitle>
                <DialogDescription>
                  Add a stock to monitor its price and performance
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleAddStock} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="symbol">Stock Symbol</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g., AAPL"
                    value={newStock.symbol}
                    onChange={(e) => setNewStock(prev => ({ ...prev, symbol: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="watchlist_name">Watchlist Name</Label>
                  <Input
                    id="watchlist_name"
                    placeholder="My Watchlist"
                    value={newStock.watchlist_name}
                    onChange={(e) => setNewStock(prev => ({ ...prev, watchlist_name: e.target.value }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="notes">Notes (Optional)</Label>
                  <Textarea
                    id="notes"
                    placeholder="Add notes about this stock..."
                    value={newStock.notes}
                    onChange={(e) => setNewStock(prev => ({ ...prev, notes: e.target.value }))}
                    rows={3}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="alert_price">Alert Price (Optional)</Label>
                  <Input
                    id="alert_price"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={newStock.alert_price}
                    onChange={(e) => setNewStock(prev => ({ ...prev, alert_price: e.target.value }))}
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setIsAddModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isAdding}>
                    {isAdding ? "Adding..." : "Add to Watchlist"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary */}
        {watchlist?.summary && (
          <div className="grid md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Stocks</p>
                    <p className="text-2xl font-bold">
                      {watchlist.summary.total_items}
                    </p>
                  </div>
                  <Star className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Gainers</p>
                    <p className="text-2xl font-bold text-green-600">
                      {watchlist.summary.gainers}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Losers</p>
                    <p className="text-2xl font-bold text-red-600">
                      {watchlist.summary.losers}
                    </p>
                  </div>
                  <TrendingDown className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">With Alerts</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {watchlist.data.filter(item => item.alert_price).length}
                    </p>
                  </div>
                  <Bell className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search watchlist..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md bg-white"
              >
                <option value="added_date">Recently Added</option>
                <option value="symbol">Symbol</option>
                <option value="price">Price</option>
                <option value="change">% Change</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Watchlist */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Star className="h-5 w-5 mr-2" />
              Your Watchlist
            </CardTitle>
            <CardDescription>
              Stocks you're monitoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sortedWatchlist.length > 0 ? (
              <>
                {/* Desktop Table */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-left p-4 font-medium">Symbol</th>
                        <th className="text-left p-4 font-medium">Company</th>
                        <th className="text-right p-4 font-medium">Price</th>
                        <th className="text-right p-4 font-medium">Change</th>
                        <th className="text-right p-4 font-medium">% Change</th>
                        <th className="text-right p-4 font-medium">Alert Price</th>
                        <th className="text-left p-4 font-medium">Notes</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortedWatchlist.map((item) => (
                        <tr key={item.id} className="border-b hover:bg-gray-50">
                          <td className="p-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <span className="font-bold text-blue-600 text-sm">
                                  {item.symbol.substring(0, 2)}
                                </span>
                              </div>
                              <div>
                                <Link
                                  to={`/app/stocks/${item.symbol}`}
                                  className="font-semibold text-blue-600 hover:underline"
                                >
                                  {item.symbol}
                                </Link>
                                <div className="text-xs text-gray-500">
                                  {item.watchlist_name}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="font-medium">{item.company_name}</div>
                          </td>
                          <td className="p-4 text-right font-medium">
                            {formatCurrency(item.current_price)}
                          </td>
                          <td className={`p-4 text-right ${
                            item.price_change >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {item.price_change >= 0 ? '+' : ''}{item.price_change?.toFixed(2)}
                          </td>
                          <td className={`p-4 text-right font-medium ${
                            item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            <div className="flex items-center justify-end">
                              {item.price_change_percent >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {formatPercentage(item.price_change_percent)}
                            </div>
                          </td>
                          <td className="p-4 text-right">
                            {item.alert_price ? (
                              <div className="flex items-center justify-end">
                                <Bell className="h-3 w-3 mr-1 text-orange-500" />
                                {formatCurrency(item.alert_price)}
                              </div>
                            ) : (
                              <span className="text-gray-400">—</span>
                            )}
                          </td>
                          <td className="p-4">
                            <div className="max-w-32 truncate text-sm text-gray-600">
                              {item.notes || '—'}
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center justify-center space-x-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleCreateAlert(item.symbol, item.current_price)}
                                title="Create Alert"
                              >
                                <Bell className="h-4 w-4" />
                              </Button>
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
                                onClick={() => handleRemoveStock(item.id, item.symbol)}
                                title="Remove from Watchlist"
                                className="text-red-600 hover:text-red-700"
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

                {/* Mobile Card View */}
                <div className="lg:hidden space-y-4">
                  {sortedWatchlist.map((item) => (
                    <Card key={item.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                              <span className="font-bold text-blue-600">
                                {item.symbol.substring(0, 2)}
                              </span>
                            </div>
                            <div>
                              <Link
                                to={`/app/stocks/${item.symbol}`}
                                className="font-semibold text-blue-600 hover:underline"
                              >
                                {item.symbol}
                              </Link>
                              <div className="text-sm text-gray-600">{item.company_name}</div>
                              <div className="text-xs text-gray-500">{item.watchlist_name}</div>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="font-semibold text-lg">
                              {formatCurrency(item.current_price)}
                            </div>
                            <div className={`text-sm font-medium flex items-center justify-end ${
                              item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {item.price_change_percent >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {formatPercentage(item.price_change_percent)}
                            </div>
                          </div>
                        </div>
                        
                        {item.notes && (
                          <div className="mb-3">
                            <div className="text-xs text-gray-500 mb-1">Notes:</div>
                            <div className="text-sm text-gray-700">{item.notes}</div>
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-600">
                            {item.alert_price && (
                              <div className="flex items-center">
                                <Bell className="h-3 w-3 mr-1 text-orange-500" />
                                Alert: {formatCurrency(item.alert_price)}
                              </div>
                            )}
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleCreateAlert(item.symbol, item.current_price)}
                            >
                              <Bell className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="ghost" asChild>
                              <Link to={`/app/stocks/${item.symbol}`}>
                                <Eye className="h-4 w-4" />
                              </Link>
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleRemoveStock(item.id, item.symbol)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <Star className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {searchTerm ? "No stocks found" : "No stocks in watchlist"}
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm 
                    ? "Try adjusting your search terms"
                    : "Add stocks to monitor their performance and get alerts"
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