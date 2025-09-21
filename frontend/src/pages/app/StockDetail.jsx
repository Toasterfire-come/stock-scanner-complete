import React, { useState, useEffect } from "react";
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
import { getStock, getRealTimeQuote, addWatchlist, createAlert } from "../../api/client";
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
        } else {
          setStockData(null);
        }

        if (realtimeResponse) {
          setRealtimeData(realtimeResponse);
        }
      } catch (error) {
        toast.error("Failed to load stock data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStockData();

    // Load chart data from Yahoo Finance chart API
    const loadChart = async () => {
      try {
        setIsChartLoading(true);
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=6mo&interval=1d`;
        const r = await fetch(url, { mode: 'cors' });
        const json = await r.json();
        const result = ((((json || {}).chart || {}).result || [])[0]) || {};
        const ts = (result.timestamp || []);
        const closes = (((result.indicators || {}).quote || [])[0] || {}).close || [];
        const volumes = (((result.indicators || {}).quote || [])[0] || {}).volume || [];
        const points = ts.map((t, i) => ({
          date: new Date(t * 1000),
          close: Number(closes[i] ?? 0),
          volume: Number(volumes[i] ?? 0)
        })).filter(p => Number.isFinite(p.close) && p.close > 0);
        setChartData(points);
      } catch (_) {
        setChartData([]);
      } finally {
        setIsChartLoading(false);
      }
    };
    loadChart();

    // Load news via stock news endpoint if needed (handled by StockNewsIntegration component)

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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

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
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Stock data not found for symbol "{symbol}". Please check the symbol and try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentData = realtimeData || stockData;
  const isPositive = currentData.change_percent >= 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
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
            <div className="flex items-center justify-between">
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
                    {formatCurrency(currentData.current_price)}
                  </div>
                  <div className={`flex items-center text-lg font-semibold ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {isPositive ? (
                      <TrendingUp className="h-5 w-5 mr-1" />
                    ) : (
                      <TrendingDown className="h-5 w-5 mr-1" />
                    )}
                    {isPositive ? '+' : ''}{currentData.price_change_today?.toFixed(2)} 
                    ({isPositive ? '+' : ''}{currentData.change_percent?.toFixed(2)}%)
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button onClick={handleAddToWatchlist} variant="outline">
                  <Star className="h-4 w-4 mr-2" />
                  Watch
                </Button>
                <Button onClick={handleCreateAlert} variant="outline">
                  <Bell className="h-4 w-4 mr-2" />
                  Alert
                </Button>
              </div>
            </div>
            
            <div className="mt-4 text-sm text-gray-500">
              Last updated: {new Date(currentData.last_updated).toLocaleString()}
            </div>

            {/* Striped details table */}
            <div className="mt-6 overflow-hidden border rounded-lg">
              <table className="min-w-full text-sm">
                <tbody className="divide-y">
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">Exchange</td>
                    <td className="p-3 font-medium">{stockData.exchange}</td>
                  </tr>
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">Currency</td>
                    <td className="p-3 font-medium">{stockData.currency || 'USD'}</td>
                  </tr>
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">Market Cap</td>
                    <td className="p-3 font-medium">{formatMarketCap(currentData.market_cap)}</td>
                  </tr>
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">Volume</td>
                    <td className="p-3 font-medium">{formatVolume(currentData.volume)}</td>
                  </tr>
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">P/E Ratio</td>
                    <td className="p-3 font-medium">{Number.isFinite(currentData.pe_ratio) ? currentData.pe_ratio.toFixed(2) : 'N/A'}</td>
                  </tr>
                  <tr className="odd:bg-gray-50">
                    <td className="p-3 text-gray-600">Dividend Yield</td>
                    <td className="p-3 font-medium">{Number.isFinite(currentData.dividend_yield) ? `${currentData.dividend_yield.toFixed(2)}%` : 'N/A'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="chart">Chart</TabsTrigger>
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
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      <BarChart3 className="h-12 w-12 mb-4" />
                      <p>Chart integration coming soon</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="chart" className="space-y-4">
                <GoogleFinanceChart 
                  symbol={symbol} 
                  height={500}
                  showControls={true}
                />
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