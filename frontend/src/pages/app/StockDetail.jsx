import React, { useState, useEffect } from "react";
import SEO from "../../components/SEO";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  AreaChart
} from "recharts";
import { Skeleton } from "../../components/ui/skeleton";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { 
  ArrowLeft,
  TrendingUp, 
  TrendingDown,
  Star,
  Bell,
  Plus,
  BarChart3,
  Activity,
  DollarSign,
  Volume2,
  Target,
  Calendar,
  Building,
  Users,
  AlertTriangle,
  ExternalLink
} from "lucide-react";
import { getStock, getRealTimeQuote, addWatchlist, createAlert, getInsiderTrades } from "../../api/client";
import { isMissing, formatCurrencySafe, formatNumberSafe } from "../../lib/utils";
import GoogleFinanceChart from "../../components/GoogleFinanceChart";
import StockNewsIntegration from "../../components/StockNewsIntegration";

const StockDetail = () => {
  const { symbol } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  const [stockData, setStockData] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [chartData, setChartData] = useState([]);
  const [isChartLoading, setIsChartLoading] = useState(false);
  const [newsItems, setNewsItems] = useState([]);
  const [insiders, setInsiders] = useState({ loading: true, data: null, error: null });

  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol) return;
      
      try {
        const [stockResponse, realtimeResponse] = await Promise.all([
          getStock(symbol).catch(() => null),
          getRealTimeQuote(symbol).catch(() => null)
        ]);

        if (stockResponse?.success) {
          setStockData(stockResponse.data);
        } else if (stockResponse?.data) {
          setStockData(stockResponse.data);
        } else {
          setStockData(null);
        }

        if (realtimeResponse?.success) {
          setRealtimeData(realtimeResponse.data);
        } else if (realtimeResponse?.data) {
          setRealtimeData(realtimeResponse.data);
        } else if (realtimeResponse) {
          setRealtimeData(realtimeResponse);
        }
      } catch (error) {
        toast.error("Failed to load stock data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStockData();

    // Disable direct Yahoo Finance fetch to avoid CORS; rely on chart component fallbacks
    const loadChart = async () => {
      try {
        setIsChartLoading(true);
        setChartData([]);
      } finally {
        setIsChartLoading(false);
      }
    };
    loadChart();

    // Load news via stock news endpoint if needed (handled by StockNewsIntegration component)

    // Load insider trades
    (async () => {
      try {
        setInsiders((s) => ({ ...s, loading: true, error: null }));
        const res = await getInsiderTrades(symbol);
        setInsiders({ loading: false, data: res, error: res?.success ? null : (res?.error || 'No data') });
      } catch (e) {
        setInsiders({ loading: false, data: null, error: 'Failed to load' });
      }
    })();

    // Set up real-time updates every 30 seconds
    const interval = setInterval(async () => {
      try {
        const realtimeResponse = await getRealTimeQuote(symbol);
        if (realtimeResponse) {
          setRealtimeData(realtimeResponse);
        }
      } catch (error) {
        // Silently fail for real-time updates
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [symbol]);

  const handleAddToWatchlist = async () => {
    try {
      await addWatchlist(symbol, {
        watchlist_name: "My Watchlist",
        notes: `Added ${stockData.company_name} from stock detail page`
      });
      toast.success(`${symbol} added to watchlist`);
    } catch (error) {
      toast.error(`Failed to add ${symbol} to watchlist`);
    }
  };

  const handleCreateAlert = async () => {
    try {
      await createAlert({
        ticker: symbol,
        target_price: stockData.current_price * 1.05, // 5% above current
        condition: "above",
        email: "user@example.com" // Should come from user context
      });
      toast.success("Price alert created successfully");
    } catch (error) {
      toast.error("Failed to create price alert");
    }
  };

  const formatCurrency = (value) => formatCurrencySafe(value, 'USD', '$—');

  const formatMarketCap = (value) => {
    const v = Number(value || 0);
    if (!Number.isFinite(v)) return '$0';
    if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
    if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
    if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
    return `$${v.toLocaleString()}`;
  };

  const formatVolume = (value) => {
    const v = Number(value || 0);
    if (!Number.isFinite(v)) return '0';
    if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
    if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`;
    return v.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-20" />
            <Skeleton className="h-8 w-48" />
          </div>
          
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <Skeleton className="h-8 w-32" />
                  <Skeleton className="h-6 w-48" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-64 w-full" />
                </CardContent>
              </Card>
            </div>
            <div>
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-24" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="flex justify-between">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-16" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <SEO title={`Stock Not Found | Trade Scan Pro`} robots="noindex,follow" />
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Stock data not found for symbol "{symbol}". Please check the symbol and try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentData = { ...(stockData || {}), ...(realtimeData || {}) };
  const isPositive = Number(currentData.change_percent || 0) >= 0;

  // Build dynamic details rows from available fields
  // Use shared isMissing from utils

  const toPercent = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return null;
    // If value looks like 0-1, treat as fraction; if > 1 and < 1000, assume percent already
    const pct = n > 1 ? n : (n * 100);
    return `${pct >= 0 ? '' : ''}${pct.toFixed(2)}%`;
  };

  const safeDisplay = (value) => {
    if (Array.isArray(value)) {
      if (!value.length) return null;
      const allPrimitive = value.every(v => (['string','number','boolean'].includes(typeof v)));
      return allPrimitive ? value.join(', ') : null; // skip arrays of objects
    }
    if (typeof value === 'object') {
      return null; // skip objects to avoid React rendering errors
    }
    return value;
  };

  const pushIf = (rows, key, label, value) => {
    const display = safeDisplay(value);
    if (!isMissing(display)) rows.push({ key, label, value: display });
  };

  const detailsRows = (() => {
    const rows = [];
    // Common, nicely formatted fields first
    pushIf(rows, 'exchange', 'Exchange', currentData.exchange);
    pushIf(rows, 'currency', 'Currency', currentData.currency || 'USD');
    // Market Cap (prefer formatted)
    const marketCapDisplay = !isMissing(currentData.formatted_market_cap)
      ? currentData.formatted_market_cap
      : (!isMissing(currentData.market_cap) ? formatMarketCap(currentData.market_cap) : null);
    pushIf(rows, 'market_cap', 'Market Cap', marketCapDisplay);
    // Volume
    const vol = !isMissing(currentData.volume_today) ? currentData.volume_today : currentData.volume;
    pushIf(rows, 'volume', 'Volume', Number.isFinite(Number(vol)) ? formatVolume(vol) : vol);
    pushIf(rows, 'avg_volume_3mon', 'Avg Volume (3m)', Number.isFinite(Number(currentData.avg_volume_3mon)) ? formatVolume(currentData.avg_volume_3mon) : currentData.avg_volume_3mon);
    pushIf(rows, 'dvav', 'Volume vs Avg', Number.isFinite(Number(currentData.dvav)) ? `${(Number(currentData.dvav) * 100).toFixed(1)}%` : currentData.dvav);
    // Day range
    const dayRange = !isMissing(currentData.days_range)
      ? currentData.days_range
      : (!isMissing(currentData.days_low) && !isMissing(currentData.days_high)
          ? `${formatCurrency(currentData.days_low)} - ${formatCurrency(currentData.days_high)}`
          : null);
    pushIf(rows, 'days_range', 'Day Range', dayRange);
    // Bid/Ask
    pushIf(rows, 'bid_price', 'Bid', Number.isFinite(Number(currentData.bid_price)) ? formatCurrency(currentData.bid_price) : currentData.bid_price);
    pushIf(rows, 'ask_price', 'Ask', Number.isFinite(Number(currentData.ask_price)) ? formatCurrency(currentData.ask_price) : currentData.ask_price);
    pushIf(rows, 'bid_ask_spread', 'Bid-Ask Spread', currentData.bid_ask_spread);
    // Ratios & yields
    if (Number.isFinite(Number(currentData.pe_ratio))) {
      pushIf(rows, 'pe_ratio', 'P/E Ratio', Number(currentData.pe_ratio).toFixed(2));
    }
    if (!isMissing(currentData.dividend_yield)) {
      const dy = Number(currentData.dividend_yield);
      const dyDisplay = Number.isFinite(dy) ? (dy > 1 ? `${dy.toFixed(2)}%` : `${(dy * 100).toFixed(2)}%`) : currentData.dividend_yield;
      pushIf(rows, 'dividend_yield', 'Dividend Yield', dyDisplay);
    }
    if (Number.isFinite(Number(currentData.earnings_per_share))) {
      pushIf(rows, 'earnings_per_share', 'EPS', Number(currentData.earnings_per_share).toFixed(2));
    }
    if (Number.isFinite(Number(currentData.book_value))) {
      pushIf(rows, 'book_value', 'Book Value', formatCurrency(currentData.book_value));
    }
    if (Number.isFinite(Number(currentData.price_to_book))) {
      pushIf(rows, 'price_to_book', 'Price/Book', Number(currentData.price_to_book).toFixed(2));
    }

    // Price change summaries if available
    if (!isMissing(currentData.change_percent)) {
      const cp = toPercent(currentData.change_percent);
      if (cp) pushIf(rows, 'change_percent', 'Change (Today)', cp);
    }
    if (!isMissing(currentData.price_change_week)) {
      const val = toPercent(currentData.price_change_week);
      if (val) pushIf(rows, 'price_change_week', 'Change (Week)', val);
    }
    if (!isMissing(currentData.price_change_month)) {
      const val = toPercent(currentData.price_change_month);
      if (val) pushIf(rows, 'price_change_month', 'Change (Month)', val);
    }
    if (!isMissing(currentData.price_change_year)) {
      const val = toPercent(currentData.price_change_year);
      if (val) pushIf(rows, 'price_change_year', 'Change (Year)', val);
    }

    // Append any other non-null fields generically (avoid duplicates and noisy keys)
    const handledKeys = new Set(rows.map(r => r.key));
    const excludeKeys = new Set([
      'ticker','symbol','company_name','name','current_price','price_change_today',
      'last_updated','market_cap_change_3mon','pe_change_3mon','recent_prices'
    ]);
    Object.keys(currentData).forEach((k) => {
      if (handledKeys.has(k) || excludeKeys.has(k)) return;
      const v = currentData[k];
      if (isMissing(v)) return;
      const label = k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
      let display = safeDisplay(v);
      if (typeof v === 'number' && Number.isFinite(v)) {
        // If looks like big integer, format with commas; if between 0 and 1, maybe percent
        if (Math.abs(v) >= 1e6) display = v.toLocaleString();
        else display = v.toString();
      }
      rows.push({ key: k, label, value: display });
    });

    return rows;
  })();

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <SEO
        title={`${stockData.ticker} | ${stockData.company_name} | Trade Scan Pro`}
        description={`Live quote, key stats and news for ${stockData.company_name} (${stockData.ticker}).`}
        url={`https://tradescanpro.com/app/stocks/${encodeURIComponent(stockData.ticker)}`}
        robots="noindex,follow"
      />
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/app/stocks">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Stocks
            </Link>
          </Button>
        </div>

        {/* Stock Header */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between sm:flex-nowrap flex-wrap gap-3">
              <div className="flex items-center space-x-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <h1 className="text-3xl font-bold text-gray-900">{stockData.ticker}</h1>
                    <Badge variant="outline">{stockData.exchange}</Badge>
                  </div>
                  <h2 className="text-xl text-gray-600 mt-1">{stockData.company_name}</h2>
                </div>
                
                <div className="text-right">
                  <div className="text-3xl font-bold">
                    {Number.isFinite(Number(currentData.current_price)) ? formatCurrency(Number(currentData.current_price)) : '$0.00'}
                  </div>
                  <div className={`flex items-center text-lg font-semibold ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {isPositive ? (
                      <TrendingUp className="h-5 w-5 mr-1" />
                    ) : (
                      <TrendingDown className="h-5 w-5 mr-1" />
                    )}
                    {isPositive ? '+' : ''}{Number.isFinite(Number(currentData.price_change_today)) ? Number(currentData.price_change_today).toFixed(2) : '0.00'} 
                    ({isPositive ? '+' : ''}{Number.isFinite(Number(currentData.change_percent)) ? Number(currentData.change_percent).toFixed(2) : '0.00'}%)
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 sm:flex-nowrap flex-wrap gap-2">
                <Button asChild variant="outline">
                  <Link to={`/app/watchlists?symbol=${encodeURIComponent(symbol)}`}>
                    <Star className="h-4 w-4 mr-2" />
                    Watch
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to={`/app/alerts?ticker=${encodeURIComponent(symbol)}`}>
                  <Bell className="h-4 w-4 mr-2" />
                  Alert
                  </Link>
                </Button>
              </div>
            </div>
            
            <div className="mt-4 text-sm text-gray-500">
              Last updated: {currentData.last_updated ? new Date(currentData.last_updated).toLocaleString() : 'N/A'}
            </div>

            {/* Striped details table (dynamic) */}
            <div className="mt-6 overflow-hidden border rounded-lg">
              <table className="min-w-full text-sm">
                <tbody className="divide-y">
                  {detailsRows.map((row) => (
                    <tr key={row.key} className="odd:bg-gray-50">
                      <td className="p-3 text-gray-600">{row.label}</td>
                      <td className="p-3 font-medium">{row.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="valuation">Valuation</TabsTrigger>
                <TabsTrigger value="insiders">Insiders</TabsTrigger>
                <TabsTrigger value="news">News</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Key Statistics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <Volume2 className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-blue-600">
                          {formatVolume(currentData.volume)}
                        </div>
                        <div className="text-sm text-blue-600">Volume</div>
                      </div>
                      
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <Building className="h-6 w-6 text-green-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-green-600">
                          {formatMarketCap(currentData.market_cap)}
                        </div>
                        <div className="text-sm text-green-600">Market Cap</div>
                      </div>
                      
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <Target className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-purple-600">
                          {currentData.pe_ratio?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="text-sm text-purple-600">P/E Ratio</div>
                      </div>
                      
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <DollarSign className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-yellow-600">
                          {currentData.dividend_yield?.toFixed(2) || '0.00'}%
                        </div>
                        <div className="text-sm text-yellow-600">Dividend Yield</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Price History</CardTitle>
                    <CardDescription>Recent price movements</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <GoogleFinanceChart 
                      symbol={symbol} 
                      height={400}
                      showControls={true}
                    />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="valuation" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Fair Value (Restricted) — Subsector Multiples</CardTitle>
                    <CardDescription>
                      Based on sector/subsector P/E multiples × forward EPS
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const v = stockData?.valuation || {};
                      const fv = v.fair_value_restricted || {};
                      const items = [
                        { label: 'Low', value: fv.low },
                        { label: 'Base', value: fv.base },
                        { label: 'High', value: fv.high },
                      ].filter(x => Number.isFinite(Number(x.value)) && Number(x.value) > 0);
                      const data = items.map((x, i) => ({ name: x.label, value: Number(x.value) }));
                      if (!data.length) return <div className="text-sm text-gray-500">No fair value data yet.</div>;
                      return (
                        <div className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                              <defs>
                                <linearGradient id="colorFv" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis tickFormatter={(v)=>`$${v}`} />
                              <Tooltip formatter={(v)=>[formatCurrencySafe(v, 'USD', '$—'), 'Fair Value']} />
                              <Area type="monotone" dataKey="value" stroke="#3b82f6" fillOpacity={1} fill="url(#colorFv)" />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      );
                    })()}
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <div className="text-gray-500">Forward EPS</div>
                        <div className="font-medium">{formatNumberSafe(stockData?.valuation?.forward_eps, 2, 'N/A')}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Sector</div>
                        <div className="font-medium">{isMissing(stockData?.valuation?.sector) ? 'N/A' : stockData.valuation.sector}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">PE (Subsector Base)</div>
                        <div className="font-medium">{formatNumberSafe(stockData?.valuation?.subsector_pe_base, 1, 'N/A')}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Analyst Target</div>
                        <div className="font-medium">{formatCurrencySafe(stockData?.valuation?.analyst_target, 'USD', 'N/A')}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Fair Value (Unrestricted) — Company Trajectory</CardTitle>
                    <CardDescription>
                      Company forward P/E × forward EPS (log scale)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const v = stockData?.valuation || {};
                      const point = Number(v.fair_value_unrestricted);
                      if (!Number.isFinite(point) || point <= 0) return <div className="text-sm text-gray-500">No fair value data yet.</div>;
                      const data = [
                        { name: 'Now', value: Number(currentData.current_price) || 0 },
                        { name: 'FV', value: point },
                      ];
                      return (
                        <div className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis scale="log" domain={['auto','auto']} tickFormatter={(v)=>`$${v}`} allowDataOverflow />
                              <Tooltip formatter={(v)=>[formatCurrencySafe(v, 'USD', '$—'), 'Value']} />
                              <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      );
                    })()}
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <div className="text-gray-500">Forward P/E</div>
                        <div className="font-medium">{formatNumberSafe(stockData?.valuation?.forward_pe, 1, 'N/A')}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">RSI(14)</div>
                        <div className="font-medium">{formatNumberSafe(stockData?.valuation?.rsi14, 2, 'N/A')}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="insiders" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Insider Trades (Last 30 Days)</CardTitle>
                    <CardDescription>SEC Form 4 filings for executives and directors</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {insiders.loading ? (
                      <div className="text-sm text-gray-500">Loading insider trades...</div>
                    ) : insiders.error ? (
                      <div className="text-sm text-red-600">{insiders.error}</div>
                    ) : !insiders.data?.success ? (
                      <div className="text-sm text-gray-500">No insider data available.</div>
                    ) : (
                      <>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div className="bg-gray-50 rounded p-3">
                            <div className="text-xs text-gray-500">Signal</div>
                            <div className="text-base font-semibold">{insiders.data.summary?.signal || 'Neutral'}</div>
                          </div>
                          <div className="bg-gray-50 rounded p-3">
                            <div className="text-xs text-gray-500">Net Activity (shares)</div>
                            <div className="text-base font-semibold">{Number(insiders.data.summary?.net_insider_activity_shares || 0).toLocaleString()}</div>
                          </div>
                          <div className="bg-gray-50 rounded p-3">
                            <div className="text-xs text-gray-500">Records</div>
                            <div className="text-base font-semibold">{insiders.data.summary?.records_count || 0}</div>
                          </div>
                          <div className="bg-gray-50 rounded p-3">
                            <div className="text-xs text-gray-500">CIK</div>
                            <div className="text-base font-semibold">{insiders.data.cik}</div>
                          </div>
                        </div>
                        <div className="overflow-auto border rounded">
                          <table className="min-w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="text-left p-2">Date</th>
                                <th className="text-left p-2">Insider</th>
                                <th className="text-left p-2">Role</th>
                                <th className="text-left p-2">Type</th>
                                <th className="text-right p-2">Shares</th>
                                <th className="text-right p-2">Price</th>
                                <th className="text-right p-2">Value</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y">
                              {(insiders.data.records || []).map((r, idx) => (
                                <tr key={idx} className="odd:bg-white even:bg-gray-50">
                                  <td className="p-2 whitespace-nowrap">{r.date}</td>
                                  <td className="p-2">{r.insider_name}</td>
                                  <td className="p-2">{r.role}</td>
                                  <td className="p-2">{r.transaction_type}{r.ad ? ` (${r.ad === 'A' ? 'Buy' : (r.ad === 'D' ? 'Sell' : r.ad)})` : ''}</td>
                                  <td className="p-2 text-right">{Number(r.shares || 0).toLocaleString()}</td>
                                  <td className="p-2 text-right">{r.price != null ? `$${Number(r.price).toFixed(2)}` : '-'}</td>
                                  <td className="p-2 text-right">{r.value != null ? `$${Number(r.value).toFixed(2)}` : '-'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="news" className="space-y-4">
                <StockNewsIntegration 
                  symbol={symbol}
                  maxItems={15}
                  showHeader={false}
                />
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Open</span>
                  <span className="font-medium">{formatCurrency(currentData.current_price - (currentData.price_change_today || 0))}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">High</span>
                  <span className="font-medium">{formatCurrency(currentData.current_price * 1.02)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Low</span>
                  <span className="font-medium">{formatCurrency(currentData.current_price * 0.98)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Volume</span>
                  <span className="font-medium">{formatVolume(currentData.volume)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Volume</span>
                  <span className="font-medium">{formatVolume(currentData.volume * 0.8)}</span>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" onClick={handleAddToWatchlist}>
                  <Star className="h-4 w-4 mr-2" />
                  Add to Watchlist
                </Button>
                <Button variant="outline" className="w-full" onClick={handleCreateAlert}>
                  <Bell className="h-4 w-4 mr-2" />
                  Set Price Alert
                </Button>
                <Button variant="outline" className="w-full" asChild>
                  <a
                    href={`https://finance.yahoo.com/quote/${symbol}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View on Yahoo Finance
                  </a>
                </Button>
              </CardContent>
            </Card>

            {/* Related Stocks */}
            <Card>
              <CardHeader>
                <CardTitle>Related Stocks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <Link to="/app/stocks/AAPL" className="font-medium text-blue-600">AAPL</Link>
                    <span className="text-green-600">+1.25%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <Link to="/app/stocks/MSFT" className="font-medium text-blue-600">MSFT</Link>
                    <span className="text-red-600">-0.83%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <Link to="/app/stocks/GOOGL" className="font-medium text-blue-600">GOOGL</Link>
                    <span className="text-green-600">+2.14%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetail;