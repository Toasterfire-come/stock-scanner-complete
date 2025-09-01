import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { toast } from "sonner";
import { 
  Search, 
  TrendingUp, 
  TrendingDown, 
  Star, 
  Filter,
  Eye,
  Bookmark,
  BarChart3,
  Volume2,
  DollarSign,
  Building,
  RefreshCw
} from "lucide-react";
import { listStocks, searchStocks, addWatchlist } from "../../api/client";

const Stocks = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [stocks, setStocks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("all");
  const [sortBy, setSortBy] = useState("last_updated");
  const [sortOrder, setSortOrder] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalStocks, setTotalStocks] = useState(0);

  const stocksPerPage = 20;

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        let response;
        
        if (searchTerm.trim()) {
          setIsSearching(true);
          response = await searchStocks(searchTerm);
          if (response.success) {
            setStocks(response.results || []);
            setTotalStocks(response.count || 0);
          }
          setIsSearching(false);
        } else {
          const params = {
            limit: stocksPerPage,
            category: category === "all" ? undefined : category,
            sort_by: sortBy,
            sort_order: sortOrder,
            // Calculate offset for pagination
            offset: (currentPage - 1) * stocksPerPage
          };

          response = await listStocks(params);
          
          if (response?.success && response?.data?.length > 0) {
            setStocks(response.data || []);
            setTotalStocks(response.total_available || 0);
          } else {
            // Mock data fallback - always show demo data when API is unavailable
            setStocks([
              {
                ticker: "AAPL",
                symbol: "AAPL",
                company_name: "Apple Inc.",
                exchange: "NASDAQ",
                current_price: 175.25,
                price_change_today: 2.34,
                change_percent: 1.35,
                volume: 52341234,
                market_cap: 2800000000000,
                last_updated: "2024-03-15T15:30:00Z"
              },
              {
                ticker: "MSFT", 
                symbol: "MSFT",
                company_name: "Microsoft Corporation",
                exchange: "NASDAQ",
                current_price: 415.67,
                price_change_today: -3.21,
                change_percent: -0.77,
                volume: 41234567,
                market_cap: 3100000000000,
                last_updated: "2024-03-15T15:30:00Z"
              },
              {
                ticker: "GOOGL",
                symbol: "GOOGL",
                company_name: "Alphabet Inc.",
                exchange: "NASDAQ",
                current_price: 142.50,
                price_change_today: 4.25,
                change_percent: 3.07,
                volume: 28765432,
                market_cap: 1800000000000,
                last_updated: "2024-03-15T15:30:00Z"
              },
              {
                ticker: "TSLA",
                symbol: "TSLA", 
                company_name: "Tesla, Inc.",
                exchange: "NASDAQ",
                current_price: 248.50,
                price_change_today: 8.75,
                change_percent: 3.65,
                volume: 95432100,
                market_cap: 790000000000,
                last_updated: "2024-03-15T15:30:00Z"
              },
              {
                ticker: "AMZN",
                symbol: "AMZN",
                company_name: "Amazon.com, Inc.",
                exchange: "NASDAQ", 
                current_price: 155.89,
                price_change_today: -2.45,
                change_percent: -1.55,
                volume: 45123789,
                market_cap: 1600000000000,
                last_updated: "2024-03-15T15:30:00Z"
              }
            ]);
            setTotalStocks(500);
          }
        }
      } catch (error) {
        toast.error("Failed to load stocks");
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce search
    const timeoutId = setTimeout(fetchStocks, searchTerm ? 500 : 0);
    return () => clearTimeout(timeoutId);
  }, [searchTerm, category, sortBy, sortOrder, currentPage]);

  const handleAddToWatchlist = async (ticker, name) => {
    try {
      await addWatchlist(ticker, {
        watchlist_name: "My Watchlist",
        notes: `Added ${name} from stocks page`
      });
      toast.success(`${ticker} added to watchlist`);
    } catch (error) {
      toast.error(`Failed to add ${ticker} to watchlist`);
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

  const totalPages = Math.ceil(totalStocks / stocksPerPage);

  if (isLoading && stocks.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex gap-4">
                <Skeleton className="h-10 flex-1" />
                <Skeleton className="h-10 w-48" />
                <Skeleton className="h-10 w-32" />
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Skeleton className="h-12 w-12 rounded" />
                      <div className="space-y-2">
                        <Skeleton className="h-6 w-32" />
                        <Skeleton className="h-4 w-48" />
                      </div>
                    </div>
                    <div className="text-right space-y-2">
                      <Skeleton className="h-6 w-24" />
                      <Skeleton className="h-4 w-16" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">All Stocks</h1>
            <p className="text-gray-600 mt-2">
              Browse and search through {totalStocks.toLocaleString()} stocks
            </p>
          </div>
          
          <Button asChild>
            <Link to="/app/screeners/new">
              <Filter className="h-4 w-4 mr-2" />
              Create Screener
            </Link>
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search stocks by symbol or company name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                  {isSearching && (
                    <RefreshCw className="absolute right-3 top-3 h-4 w-4 text-gray-400 animate-spin" />
                  )}
                </div>
              </div>
              
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Stocks</SelectItem>
                  <SelectItem value="gainers">Top Gainers</SelectItem>
                  <SelectItem value="losers">Top Losers</SelectItem>
                  <SelectItem value="high_volume">High Volume</SelectItem>
                  <SelectItem value="large_cap">Large Cap</SelectItem>
                  <SelectItem value="small_cap">Small Cap</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last_updated">Recently Updated</SelectItem>
                  <SelectItem value="price">Price</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="market_cap">Market Cap</SelectItem>
                  <SelectItem value="change_percent">% Change</SelectItem>
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
          </CardContent>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Stock List
              {searchTerm && (
                <Badge variant="secondary" className="ml-2">
                  Search: "{searchTerm}"
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              {searchTerm 
                ? `Found ${stocks.length} results for "${searchTerm}"`
                : `Showing ${stocks.length} of ${totalStocks.toLocaleString()} stocks`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stocks.length === 0 ? (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No stocks found</h3>
                <p className="text-gray-600">
                  {searchTerm 
                    ? `No results found for "${searchTerm}". Try a different search term.`
                    : "No stocks available with the current filters."
                  }
                </p>
              </div>
            ) : (
              <>
                {/* Desktop Table View */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-left p-4 font-medium">Symbol</th>
                        <th className="text-left p-4 font-medium">Company</th>
                        <th className="text-right p-4 font-medium">Price</th>
                        <th className="text-right p-4 font-medium">Change</th>
                        <th className="text-right p-4 font-medium">% Change</th>
                        <th className="text-right p-4 font-medium">Volume</th>
                        <th className="text-right p-4 font-medium">Market Cap</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stocks.map((stock) => (
                        <tr key={stock.ticker} className="border-b hover:bg-gray-50">
                          <td className="p-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <span className="font-bold text-blue-600 text-sm">
                                  {stock.ticker.substring(0, 2)}
                                </span>
                              </div>
                              <div>
                                <Link
                                  to={`/app/stocks/${stock.ticker}`}
                                  className="font-semibold text-blue-600 hover:underline"
                                >
                                  {stock.ticker}
                                </Link>
                                <div className="text-xs text-gray-500">{stock.exchange}</div>
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="font-medium text-gray-900">
                              {stock.company_name}
                            </div>
                          </td>
                          <td className="p-4 text-right font-medium">
                            {formatCurrency(stock.current_price)}
                          </td>
                          <td className={`p-4 text-right ${
                            stock.price_change_today >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {stock.price_change_today >= 0 ? '+' : ''}{stock.price_change_today?.toFixed(2)}
                          </td>
                          <td className={`p-4 text-right font-medium ${
                            stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            <div className="flex items-center justify-end">
                              {stock.change_percent >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {formatPercentage(stock.change_percent)}
                            </div>
                          </td>
                          <td className="p-4 text-right text-gray-600">
                            {formatVolume(stock.volume)}
                          </td>
                          <td className="p-4 text-right text-gray-600">
                            {formatMarketCap(stock.market_cap)}
                          </td>
                          <td className="p-4">
                            <div className="flex items-center justify-center space-x-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleAddToWatchlist(stock.ticker, stock.company_name)}
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

                {/* Mobile Card View */}
                <div className="lg:hidden space-y-4">
                  {stocks.map((stock) => (
                    <Card key={stock.ticker} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                              <span className="font-bold text-blue-600">
                                {stock.ticker.substring(0, 2)}
                              </span>
                            </div>
                            <div>
                              <Link
                                to={`/app/stocks/${stock.ticker}`}
                                className="font-semibold text-blue-600 hover:underline"
                              >
                                {stock.ticker}
                              </Link>
                              <div className="text-sm text-gray-600">{stock.company_name}</div>
                              <div className="text-xs text-gray-500">{stock.exchange}</div>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="font-semibold text-lg">
                              {formatCurrency(stock.current_price)}
                            </div>
                            <div className={`text-sm font-medium flex items-center justify-end ${
                              stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {stock.change_percent >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {formatPercentage(stock.change_percent)}
                            </div>
                            <div className="text-xs text-gray-500">
                              Vol: {formatVolume(stock.volume)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between mt-4">
                          <div className="text-sm text-gray-600">
                            Market Cap: {formatMarketCap(stock.market_cap)}
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleAddToWatchlist(stock.ticker, stock.company_name)}
                            >
                              <Bookmark className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="ghost" asChild>
                              <Link to={`/app/stocks/${stock.ticker}`}>
                                <Eye className="h-4 w-4" />
                              </Link>
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Pagination */}
                {!searchTerm && totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6">
                    <div className="text-sm text-gray-600">
                      Showing {((currentPage - 1) * stocksPerPage) + 1} to {Math.min(currentPage * stocksPerPage, totalStocks)} of {totalStocks.toLocaleString()} stocks
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        Previous
                      </Button>
                      
                      <div className="flex space-x-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          const page = Math.max(1, currentPage - 2) + i;
                          if (page > totalPages) return null;
                          
                          return (
                            <Button
                              key={page}
                              variant={page === currentPage ? "default" : "outline"}
                              size="sm"
                              onClick={() => handlePageChange(page)}
                            >
                              {page}
                            </Button>
                          );
                        })}
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Stocks;