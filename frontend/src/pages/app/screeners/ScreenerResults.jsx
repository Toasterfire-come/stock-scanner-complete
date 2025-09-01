import React, { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Skeleton } from "../../../components/ui/skeleton";
import { toast } from "sonner";
import { 
  ArrowLeft, 
  Download, 
  RefreshCw, 
  Star, 
  TrendingUp, 
  TrendingDown,
  Plus,
  ExternalLink,
  Filter,
  Eye,
  Bookmark,
  BarChart3
} from "lucide-react";
import { filterStocks, addWatchlist } from "../../../api/client";

const ScreenerResults = () => {
  const { id } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [results, setResults] = useState([]);
  const [screenerInfo, setScreenerInfo] = useState(null);
  const [sortBy, setSortBy] = useState("change_percent");
  const [sortOrder, setSortOrder] = useState("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRows, setSelectedRows] = useState(new Set());

  useEffect(() => {
    const fetchResults = async () => {
      try {
        // Mock screener info
        setScreenerInfo({
          id,
          name: id === "preview" ? "Preview Results" : "High Growth Tech Stocks",
          description: "Technology companies with revenue growth > 25% and P/E < 30",
          category: "Growth",
          criteria_count: 8,
          last_run: new Date().toISOString(),
          tags: ["tech", "growth", "high-volume"]
        });

        // Use the Django filter endpoint for results
        const response = await filterStocks({
          min_price: 10,
          max_price: 500,
          min_volume: 100000,
          order_by: sortBy,
          limit: 50
        });

        if (response.stocks) {
          setResults(response.stocks);
        } else {
          // Mock data fallback
          setResults([
            {
              ticker: "AAPL",
              name: "Apple Inc.",
              current_price: 175.25,
              price_change: 2.34,
              price_change_percent: 1.35,
              volume: 52341234,
              market_cap: 2800000000000,
              exchange: "NASDAQ"
            },
            {
              ticker: "MSFT", 
              name: "Microsoft Corporation",
              current_price: 415.67,
              price_change: -3.21,
              price_change_percent: -0.77,
              volume: 41234567,
              market_cap: 3100000000000,
              exchange: "NASDAQ"
            },
            {
              ticker: "GOOGL",
              name: "Alphabet Inc.",
              current_price: 142.50,
              price_change: 4.25,
              price_change_percent: 3.07,
              volume: 28765432,
              market_cap: 1800000000000,
              exchange: "NASDAQ"
            },
            {
              ticker: "NVDA",
              name: "NVIDIA Corporation", 
              current_price: 875.43,
              price_change: 15.67,
              price_change_percent: 1.82,
              volume: 65432109,
              market_cap: 2200000000000,
              exchange: "NASDAQ"
            },
            {
              ticker: "META",
              name: "Meta Platforms Inc.",
              current_price: 485.12,
              price_change: -8.43,
              price_change_percent: -1.71,
              volume: 35678901,
              market_cap: 1250000000000,
              exchange: "NASDAQ"
            }
          ]);
        }
      } catch (error) {
        toast.error("Failed to load screener results");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [id, sortBy]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success("Results refreshed");
    } catch (error) {
      toast.error("Failed to refresh results");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleAddToWatchlist = async (ticker, name) => {
    try {
      await addWatchlist(ticker, {
        watchlist_name: "My Watchlist",
        notes: `Added from screener: ${screenerInfo?.name}`
      });
      toast.success(`${ticker} added to watchlist`);
    } catch (error) {
      toast.error(`Failed to add ${ticker} to watchlist`);
    }
  };

  const handleSelectRow = (ticker) => {
    setSelectedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ticker)) {
        newSet.delete(ticker);
      } else {
        newSet.add(ticker);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedRows.size === filteredResults.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(filteredResults.map(r => r.ticker)));
    }
  };

  const handleBulkAddToWatchlist = async () => {
    const selectedTickers = Array.from(selectedRows);
    try {
      for (const ticker of selectedTickers) {
        await addWatchlist(ticker, {
          watchlist_name: "My Watchlist",
          notes: `Bulk added from screener: ${screenerInfo?.name}`
        });
      }
      toast.success(`${selectedTickers.length} stocks added to watchlist`);
      setSelectedRows(new Set());
    } catch (error) {
      toast.error("Failed to add stocks to watchlist");
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

  const filteredResults = results.filter(stock => 
    stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedResults = [...filteredResults].sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-20" />
            <Skeleton className="h-8 w-64" />
          </div>
          
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-96" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/app/screeners">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Screeners
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{screenerInfo?.name}</h1>
            <p className="text-gray-600 mt-2">{screenerInfo?.description}</p>
          </div>
        </div>

        {/* Screener Info */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div>
                  <div className="text-2xl font-bold text-blue-600">{results.length}</div>
                  <div className="text-sm text-gray-600">Matching Stocks</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{screenerInfo?.criteria_count}</div>
                  <div className="text-sm text-gray-600">Criteria</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Last Run</div>
                  <div className="font-medium">
                    {new Date(screenerInfo?.last_run).toLocaleString()}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {screenerInfo?.tags?.map((tag) => (
                    <Badge key={tag} variant="secondary">{tag}</Badge>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                  {isRefreshing ? 'Refreshing...' : 'Refresh'}
                </Button>
                
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Controls */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Input
                    placeholder="Search stocks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-64"
                  />
                </div>
                
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ticker">Ticker</SelectItem>
                    <SelectItem value="name">Company Name</SelectItem>
                    <SelectItem value="current_price">Price</SelectItem>
                    <SelectItem value="price_change_percent">% Change</SelectItem>
                    <SelectItem value="volume">Volume</SelectItem>
                    <SelectItem value="market_cap">Market Cap</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={sortOrder} onValueChange={setSortOrder}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="desc">Desc</SelectItem>
                    <SelectItem value="asc">Asc</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {selectedRows.size > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {selectedRows.size} selected
                  </span>
                  <Button size="sm" onClick={handleBulkAddToWatchlist}>
                    <Bookmark className="h-4 w-4 mr-2" />
                    Add to Watchlist
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Screening Results
            </CardTitle>
            <CardDescription>
              Stocks matching your screening criteria
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sortedResults.length === 0 ? (
              <div className="text-center py-12">
                <Filter className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
                <p className="text-gray-600">
                  Try adjusting your search or screening criteria
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left p-3">
                        <input
                          type="checkbox"
                          checked={selectedRows.size === filteredResults.length}
                          onChange={handleSelectAll}
                          className="rounded"
                        />
                      </th>
                      <th className="text-left p-3 font-medium">Symbol</th>
                      <th className="text-left p-3 font-medium">Company</th>
                      <th className="text-right p-3 font-medium">Price</th>
                      <th className="text-right p-3 font-medium">Change</th>
                      <th className="text-right p-3 font-medium">% Change</th>
                      <th className="text-right p-3 font-medium">Volume</th>
                      <th className="text-right p-3 font-medium">Market Cap</th>
                      <th className="text-center p-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedResults.map((stock) => (
                      <tr key={stock.ticker} className="border-b hover:bg-gray-50">
                        <td className="p-3">
                          <input
                            type="checkbox"
                            checked={selectedRows.has(stock.ticker)}
                            onChange={() => handleSelectRow(stock.ticker)}
                            className="rounded"
                          />
                        </td>
                        <td className="p-3">
                          <Link
                            to={`/app/stocks/${stock.ticker}`}
                            className="font-semibold text-blue-600 hover:underline"
                          >
                            {stock.ticker}
                          </Link>
                          <div className="text-xs text-gray-500">{stock.exchange}</div>
                        </td>
                        <td className="p-3">
                          <div className="font-medium">{stock.name}</div>
                        </td>
                        <td className="p-3 text-right font-medium">
                          {formatCurrency(stock.current_price)}
                        </td>
                        <td className={`p-3 text-right ${
                          stock.price_change >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {stock.price_change >= 0 ? '+' : ''}{stock.price_change?.toFixed(2)}
                        </td>
                        <td className={`p-3 text-right font-medium ${
                          stock.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          <div className="flex items-center justify-end">
                            {stock.price_change_percent >= 0 ? (
                              <TrendingUp className="h-3 w-3 mr-1" />
                            ) : (
                              <TrendingDown className="h-3 w-3 mr-1" />
                            )}
                            {stock.price_change_percent >= 0 ? '+' : ''}{stock.price_change_percent?.toFixed(2)}%
                          </div>
                        </td>
                        <td className="p-3 text-right text-gray-600">
                          {formatVolume(stock.volume)}
                        </td>
                        <td className="p-3 text-right text-gray-600">
                          {formatMarketCap(stock.market_cap)}
                        </td>
                        <td className="p-3">
                          <div className="flex items-center justify-center space-x-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleAddToWatchlist(stock.ticker, stock.name)}
                              title="Add to Watchlist"
                            >
                              <Star className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              asChild
                              title="View Details"
                            >
                              <Link to={`/app/stocks/${stock.ticker}`}>
                                <Eye className="h-4 w-4" />
                              </Link>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ScreenerResults;