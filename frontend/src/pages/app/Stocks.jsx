import React, { useState, useEffect, useMemo } from "react";
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
  Filter,
  Eye,
  Bookmark,
  BarChart3,
  RefreshCw
} from "lucide-react";
import { listStocks, searchStocks, addWatchlist, fetchAllStocks, getTotalTickers } from "../../api/client";
import { announce } from "../../lib/a11y";
import VirtualizedList from "../../components/VirtualizedList";

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
  const [totalTickersInDB, setTotalTickersInDB] = useState(0);

  const stocksPerPage = 50; // fixed page size, client-side pagination
  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const SortHeader = ({ field, children, align = 'left' }) => (
    <th className={`p-4 font-medium text-${align}`}> 
      <button onClick={() => toggleSort(field)} className="inline-flex items-center gap-1 hover:text-blue-600">
        <span>{children}</span>
        {sortBy === field && (
          <span className="text-xs text-muted-foreground">{sortOrder === 'asc' ? '▲' : '▼'}</span>
        )}
      </button>
    </th>
  );

  // Fetch total tickers count from database
  useEffect(() => {
    const fetchTotalTickers = async () => {
      try {
        const response = await getTotalTickers();
        if (response.success) {
          setTotalTickersInDB(response.total_tickers || 0);
        }
      } catch (error) {
        // Silently handle error, keep default 0
      }
    };
    fetchTotalTickers();
  }, []);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        // Always fetch the full set needed locally, then sort/paginate client-side
        setIsSearching(Boolean(searchTerm.trim()));
        let universe;
        if (searchTerm.trim()) {
          const resp = await searchStocks(searchTerm.trim());
          universe = Array.isArray(resp) ? resp : (resp?.results || resp?.data || []);
        } else {
          // Pull all stocks for the active category; backend can still filter by category, but no blank params
          const baseParams = { category: category === 'all' ? undefined : category };
          universe = await fetchAllStocks(baseParams);
        }
        const items = Array.isArray(universe) ? universe : [];
        // Normalize numeric fields for reliable sorting
        const normalized = items.map((s) => ({
          ...s,
          current_price: Number(s.current_price ?? s.price ?? 0),
          price_change_today: Number(s.price_change_today ?? 0),
          change_percent: Number(s.change_percent ?? 0),
          volume: Number(s.volume ?? 0),
          market_cap: Number(s.market_cap ?? 0),
        }));

        // Sort client-side
        const sortKey = {
          last_updated: (a) => new Date(a.last_updated || a.updated_at || 0).getTime(),
          price: (a) => a.current_price,
          volume: (a) => a.volume,
          market_cap: (a) => a.market_cap,
          change_percent: (a) => a.change_percent,
        }[sortBy] || ((a) => new Date(a.last_updated || a.updated_at || 0).getTime());

        const sorted = normalized.sort((a, b) => {
          const av = sortKey(a);
          const bv = sortKey(b);
          return sortOrder === 'asc' ? av - bv : bv - av;
        });

        setTotalStocks(sorted.length);
        // Client-side pagination slice
        const start = (currentPage - 1) * stocksPerPage;
        const pageItems = sorted.slice(start, start + stocksPerPage);
        setStocks(pageItems);
        setIsSearching(false);
      } catch (error) {
        toast.error("Failed to load stocks");
      } finally {
        setIsLoading(false);
      }
    };
    const t = setTimeout(fetchStocks, searchTerm ? 300 : 0);
    return () => clearTimeout(t);
  }, [searchTerm, category, sortBy, sortOrder, currentPage]);

  const handleAddToWatchlist = async (ticker, name) => {
    try {
      await addWatchlist(ticker, { watchlist_name: "My Watchlist", notes: `Added ${name} from stocks page` });
      toast.success(`${ticker} added to watchlist`);
      try { announce(`${ticker} added to watchlist`); } catch {}
    } catch (error) {
      toast.error(`Failed to add ${ticker} to watchlist`);
      try { announce(`Failed to add ${ticker} to watchlist`); } catch {}
    }
  };

  const handlePageChange = (newPage) => { setCurrentPage(newPage); window.scrollTo({ top: 0, behavior: 'smooth' }); };

  const totalPages = Math.max(1, Math.ceil(totalStocks / stocksPerPage));

  // client-side pagination when searching
  const pagedSearchStocks = useMemo(() => {
    if (!searchTerm) return stocks;
    const start = (currentPage - 1) * stocksPerPage;
    return stocks.slice(start, start + stocksPerPage);
  }, [stocks, searchTerm, currentPage]);

  const dataForRender = stocks;
  const isVirtualDesktop = totalStocks > 200;

  const formatCurrency = (value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value || 0));
  const formatVolume = (v) => { const n = Number(v||0); if (!Number.isFinite(n)) return '0'; if (n>=1e9) return `${(n/1e9).toFixed(1)}B`; if (n>=1e6) return `${(n/1e6).toFixed(1)}M`; if (n>=1e3) return `${(n/1e3).toFixed(0)}K`; return n.toLocaleString(); };
  const formatMarketCap = (v) => { const n = Number(v||0); if (!Number.isFinite(n)) return '$0'; if (n>=1e12) return `$${(n/1e12).toFixed(1)}T`; if (n>=1e9) return `$${(n/1e9).toFixed(1)}B`; if (n>=1e6) return `$${(n/1e6).toFixed(1)}M`; return `$${n.toLocaleString()}`; };
  const formatPercentage = (v) => `${(Number(v)||0) > 0 ? '+' : ''}${(Number(v)||0).toFixed(2)}%`;

  if (isLoading && dataForRender.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          <Card><CardContent className="p-6"><div className="flex gap-4"><Skeleton className="h-10 flex-1" /><Skeleton className="h-10 w-48" /><Skeleton className="h-10 w-32" /></div></CardContent></Card>
          <div className="grid gap-4">{[1,2,3,4,5].map(i => <Card key={i}><CardContent className="p-6"><div className="flex items-center justify-between"><div className="flex items-center space-x-4"><Skeleton className="h-12 w-12 rounded" /><div className="space-y-2"><Skeleton className="h-6 w-32" /><Skeleton className="h-4 w-48" /></div></div><div className="text-right space-y-2"><Skeleton className="h-6 w-24" /><Skeleton className="h-4 w-16" /></div></div></CardContent></Card>)}</div>
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
            <p className="text-gray-600 mt-2">Browse and search through {Number(totalStocks||0).toLocaleString()} stocks</p>
          </div>
          <Button asChild><Link to="/app/screeners/new"><Filter className="h-4 w-4 mr-2" />Create Screener</Link></Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input placeholder="Search stocks by symbol or company name..." value={searchTerm} onChange={(e) => { setCurrentPage(1); setSearchTerm(e.target.value); }} className="pl-10" />
                  {isSearching && <RefreshCw className="absolute right-3 top-3 h-4 w-4 text-gray-400 animate-spin" />}
                </div>
              </div>
              <Select value={category} onValueChange={(v) => { setCurrentPage(1); setCategory(v); }}>
                <SelectTrigger className="w-48"><SelectValue placeholder="Category" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Stocks</SelectItem>
                  <SelectItem value="gainers">Top Gainers</SelectItem>
                  <SelectItem value="losers">Top Losers</SelectItem>
                  <SelectItem value="high_volume">High Volume</SelectItem>
                  <SelectItem value="large_cap">Large Cap</SelectItem>
                  <SelectItem value="small_cap">Small Cap</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortBy} onValueChange={(v) => { setCurrentPage(1); setSortBy(v); }}>
                <SelectTrigger className="w-48"><SelectValue placeholder="Sort by" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="last_updated">Recently Updated</SelectItem>
                  <SelectItem value="price">Price</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="market_cap">Market Cap</SelectItem>
                  <SelectItem value="change_percent">% Change</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortOrder} onValueChange={(v) => { setCurrentPage(1); setSortOrder(v); }}>
                <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
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
            <CardTitle className="flex items-center"><BarChart3 className="h-5 w-5 mr-2" />Stock List {searchTerm && (<Badge variant="secondary" className="ml-2">Search: "{searchTerm}"</Badge>)}</CardTitle>
            <CardDescription>{searchTerm ? `Showing ${dataForRender.length} of ${Number(totalStocks||0)} results` : `Showing ${dataForRender.length} of ${Number(totalStocks||0).toLocaleString()} stocks`}</CardDescription>
          </CardHeader>
          <CardContent>
            {dataForRender.length === 0 ? (
              <div className="text-center py-12"><Search className="h-12 w-12 text-gray-300 mx-auto mb-4" /><h3 className="text-lg font-medium text-gray-900 mb-2">No stocks found</h3><p className="text-gray-600">{searchTerm ? `No results found for "${searchTerm}". Try a different search term.` : "No stocks available with the current filters."}</p></div>
            ) : (
              <>
                {/* Desktop: virtualized when many rows */}
                <div className="hidden lg:block">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="sticky top-0 z-10">
                        <tr className="border-b bg-gray-50">
                          <SortHeader field="ticker">Symbol</SortHeader>
                          <SortHeader field="company_name">Company</SortHeader>
                          <SortHeader field="price" align="right">Price</SortHeader>
                          <SortHeader field="price_change_today" align="right">Change</SortHeader>
                          <SortHeader field="change_percent" align="right">% Change</SortHeader>
                          <SortHeader field="volume" align="right">Volume</SortHeader>
                          <SortHeader field="market_cap" align="right">Market Cap</SortHeader>
                          <th className="text-center p-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                    </table>
                  </div>
                  {isVirtualDesktop ? (
                    <div className="border rounded">
                      <VirtualizedList
                        items={dataForRender}
                        itemSize={56}
                        height={560}
                        row={({ index, style, item: stock }) => (
                          <div className="border-b hover:bg-gray-50 grid" style={{...style, display:'grid', gridTemplateColumns:'2fr 3fr 1fr 1fr 1fr 1fr 1fr 1fr', alignItems:'center'}}>
                            <div className="p-4 flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><span className="font-bold text-blue-600 text-sm">{stock.ticker?.substring(0,2)}</span></div>
                              <div>
                                <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                                <div className="text-xs text-gray-500">{stock.exchange}</div>
                              </div>
                            </div>
                            <div className="p-4 font-medium text-gray-900">{stock.company_name}</div>
                            <div className="p-4 text-right font-medium">{stock.formatted_price || formatCurrency(stock.current_price)}</div>
                            <div className={`p-4 text-right ${(stock.is_gaining ?? (Number(stock.price_change_today)>=0)) ? 'text-green-600':'text-red-600'}`}>{(stock.price_change_today ?? 0) >= 0 ? '+' : ''}{Number(stock.price_change_today||0).toFixed(2)}</div>
                            <div className={`p-4 text-right font-medium ${(stock.is_gaining ?? (Number(stock.change_percent)>=0)) ? 'text-green-600':'text-red-600'}`}>
                              {stock.formatted_change || formatPercentage(stock.change_percent)}
                            </div>
                            <div className="p-4 text-right text-gray-600">{stock.formatted_volume || formatVolume(stock.volume)}</div>
                            <div className="p-4 text-right text-gray-600">{stock.formatted_market_cap || formatMarketCap(stock.market_cap)}</div>
                            <div className="p-4 flex items-center justify-center space-x-2">
                              <Button size="sm" variant="ghost" aria-label={`Add ${stock.ticker} to watchlist`} onClick={() => handleAddToWatchlist(stock.ticker, stock.company_name)} title="Add to Watchlist"><Bookmark className="h-4 w-4" aria-hidden="true" /></Button>
                              <Button size="sm" variant="ghost" asChild aria-label={`View ${stock.ticker} details`} title="View Details"><Link to={`/app/stocks/${stock.ticker}`}><Eye className="h-4 w-4" aria-hidden="true" /></Link></Button>
                            </div>
                          </div>
                        )}
                      />
                    </div>
                  ) : (
                    <div className="hidden lg:block overflow-x-auto">
                      <table className="w-full">
                        <tbody>
                          {dataForRender.map((stock) => (
                            <tr key={stock.ticker} className="border-b hover:bg-gray-50">
                              <td className="p-4">
                                <div className="flex items-center space-x-3">
                                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><span className="font-bold text-blue-600 text-sm">{stock.ticker.substring(0, 2)}</span></div>
                                  <div>
                                    <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                                    <div className="text-xs text-gray-500">{stock.exchange}</div>
                                  </div>
                                </div>
                              </td>
                              <td className="p-4"><div className="font-medium text-gray-900">{stock.company_name}</div></td>
                              <td className="p-4 text-right font-medium">{stock.formatted_price || formatCurrency(stock.current_price)}</td>
                              <td className={`p-4 text-right ${(stock.is_gaining ?? (Number(stock.price_change_today)>=0)) ? 'text-green-600' : 'text-red-600'}`}>{(stock.price_change_today ?? 0) >= 0 ? '+' : ''}{stock.price_change_today?.toFixed(2)}</td>
                              <td className={`p-4 text-right font-medium ${(stock.is_gaining ?? (Number(stock.change_percent)>=0)) ? 'text-green-600' : 'text-red-600'}`}>
                                <div className="flex items-center justify-end">{(stock.is_gaining ?? (Number(stock.change_percent)>=0)) ? (<TrendingUp className="h-3 w-3 mr-1" aria-hidden="true" />) : (<TrendingDown className="h-3 w-3 mr-1" aria-hidden="true" />)}{stock.formatted_change || formatPercentage(stock.change_percent)}</div>
                              </td>
                              <td className="p-4 text-right text-gray-600">{stock.formatted_volume || formatVolume(stock.volume)}</td>
                              <td className="p-4 text-right text-gray-600">{stock.formatted_market_cap || formatMarketCap(stock.market_cap)}</td>
                              <td className="p-4"><div className="flex items-center justify-center space-x-2"><Button size="sm" variant="ghost" aria-label={`Add ${stock.ticker} to watchlist`} onClick={() => handleAddToWatchlist(stock.ticker, stock.company_name)} title="Add to Watchlist"><Bookmark className="h-4 w-4" aria-hidden="true" /></Button><Button size="sm" variant="ghost" asChild aria-label={`View ${stock.ticker} details`} title="View Details"><Link to={`/app/stocks/${stock.ticker}`}><Eye className="h-4 w-4" aria-hidden="true" /></Link></Button></div></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                {/* Mobile Cards */}
                <div className="lg:hidden space-y-4">
                  {dataForRender.map((stock) => (
                    <Card key={stock.ticker} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"><span className="font-bold text-blue-600">{stock.ticker.substring(0, 2)}</span></div>
                            <div>
                              <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                              <div className="text-sm text-gray-600">{stock.company_name}</div>
                              <div className="text-xs text-gray-500">{stock.exchange}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-lg">{stock.formatted_price || formatCurrency(stock.current_price)}</div>
                            <div className={`text-sm font-medium flex items-center justify-end ${(stock.is_gaining ?? (Number(stock.change_percent)>=0)) ? 'text-green-600' : 'text-red-600'}`}>{(stock.is_gaining ?? (Number(stock.change_percent)>=0)) ? (<TrendingUp className="h-3 w-3 mr-1" />) : (<TrendingDown className="h-3 w-3 mr-1" />)}{stock.formatted_change || formatPercentage(stock.change_percent)}</div>
                            <div className="text-xs text-gray-500">Vol: {stock.formatted_volume || formatVolume(stock.volume)}</div>
                          </div>
                        </div>
                        <div className="flex items-center justify-between mt-4">
                          <div className="text-sm text-gray-600">Market Cap: {stock.formatted_market_cap || formatMarketCap(stock.market_cap)}</div>
                          <div className="flex space-x-2"><Button size="sm" variant="ghost" onClick={() => handleAddToWatchlist(stock.ticker, stock.company_name)}><Bookmark className="h-4 w-4" /></Button><Button size="sm" variant="ghost" asChild><Link to={`/app/stocks/${stock.ticker}`}><Eye className="h-4 w-4" /></Link></Button></div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6">
                    <div className="text-sm text-gray-600">Showing {((currentPage - 1) * stocksPerPage) + 1} to {Math.min(currentPage * stocksPerPage, Number(totalStocks||0))} of {Number(totalStocks||0).toLocaleString()} stocks</div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>Previous</Button>
                      <div className="flex space-x-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => { const page = Math.max(1, currentPage - 2) + i; if (page > totalPages) return null; return (<Button key={page} variant={page === currentPage ? "default" : "outline"} size="sm" onClick={() => handlePageChange(page)}>{page}</Button>); })}
                      </div>
                      <Button variant="outline" size="sm" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>Next</Button>
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