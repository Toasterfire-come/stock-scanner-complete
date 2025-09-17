import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Skeleton } from "../../components/ui/skeleton";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Activity, 
  Globe,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  Clock
} from "lucide-react";
import { getMarketStatsSafe, getTrendingSafe, getStatisticsSafe, getDashboardStats } from "../../api/client";
import { toast } from "sonner";

const Markets = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [marketStats, setMarketStats] = useState(null);
  const [trending, setTrending] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMarketData = async () => {
      setError("");
      try {
        const [statsResponse, trendingResponse, statisticsResponse, dashboardStatsResponse] = await Promise.all([
          getMarketStatsSafe(),
          getTrendingSafe(),
          getStatisticsSafe(),
          getDashboardStats(),
        ]);

        if (!statsResponse.success) {
          setError((e) => e || statsResponse.error);
          toast.error(statsResponse.error);
        }
        if (!trendingResponse.success) {
          setError((e) => e || trendingResponse.error);
          toast.error(trendingResponse.error);
        }
        if (!statisticsResponse.success) {
          // statistics is optional informational block
        }

        setMarketStats(statsResponse.data);
        setTrending(trendingResponse.data);
        setStatistics(statisticsResponse.data);
        setDashboardStats(dashboardStatsResponse.data);
      } catch (err) {
        const msg = "Failed to fetch market data";
        setError(msg);
        toast.error(msg);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarketData();

    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchMarketData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setError("");
    try {
      const [statsResponse, trendingResponse] = await Promise.all([
        getMarketStatsSafe(),
        getTrendingSafe(),
      ]);
      if (!statsResponse.success) toast.error(statsResponse.error);
      if (!trendingResponse.success) toast.error(trendingResponse.error);
      setMarketStats(statsResponse.data);
      setTrending(trendingResponse.data);
    } catch (err) {
      toast.error("Refresh failed");
    } finally {
      setIsRefreshing(false);
    }
  };

  const formatCurrency = (value) => {
    const v = Number(value);
    if (!Number.isFinite(v)) return "-";
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(v);
  };

  const safePct = (num, den) => {
    const n = Number(num);
    const d = Number(den);
    if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return 0;
    return (n / d) * 100;
  };

  const formatPercentage = (value) => {
    const v = Number(value);
    if (!Number.isFinite(v)) return "-";
    const sign = v > 0 ? '+' : '';
    return `${sign}${v.toFixed(1)}%`;
  };

  const formatVolume = (value) => {
    const v = Number(value);
    if (!Number.isFinite(v)) return "-";
    if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
    if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`;
    return v.toLocaleString();
  };

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
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-4 w-16" />
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex items-center justify-between">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-16" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex items-center justify-between">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-16" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
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
            <h1 className="text-3xl font-bold text-gray-900">Market Overview</h1>
            <p className="text-gray-600 mt-2">Real-time market data and trending stocks</p>
          </div>
          <Button onClick={handleRefresh} disabled={isRefreshing} variant="outline">
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {error && (
          <Card className="border-l-4 border-l-yellow-500 bg-yellow-50/50">
            <CardContent className="p-4 text-yellow-800 flex items-center justify-between">
              <span>{error}</span>
              <Button size="sm" variant="outline" onClick={handleRefresh}>Retry</Button>
            </CardContent>
          </Card>
        )}

        {/* Market Summary */}
        {marketStats && (
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Stocks</p>
                    <p className="text-2xl font-bold">{Number(dashboardStats?.totalTickers || marketStats?.market_overview?.total_stocks || 0).toLocaleString()}</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Gainers</p>
                    <div className="flex items-center">
                      <p className="text-2xl font-bold text-green-600">{Number(dashboardStats?.totalGainers || marketStats?.market_overview?.gainers || 0).toLocaleString()}</p>
                      <ArrowUpRight className="h-5 w-5 text-green-500 ml-2" />
                    </div>
                    <p className="text-xs text-green-600">{dashboardStats?.gainerPercentage?.toFixed(1) || safePct(marketStats?.market_overview?.gainers, marketStats?.market_overview?.total_stocks).toFixed(1)}%</p>
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
                    <div className="flex items-center">
                      <p className="text-2xl font-bold text-red-600">{Number(dashboardStats?.totalLosers || marketStats?.market_overview?.losers || 0).toLocaleString()}</p>
                      <ArrowDownRight className="h-5 w-5 text-red-500 ml-2" />
                    </div>
                    <p className="text-xs text-red-600">{safePct(marketStats.market_overview.losers, marketStats.market_overview.total_stocks).toFixed(1)}%</p>
                  </div>
                  <TrendingDown className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            
          </div>
        )}

        {/* Market Data Tabs */}
        <Tabs defaultValue="gainers" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="gainers">Top Gainers</TabsTrigger>
            <TabsTrigger value="losers">Top Losers</TabsTrigger>
            <TabsTrigger value="active">Most Active</TabsTrigger>
          </TabsList>

          <div className="mt-6">
            <TabsContent value="gainers">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2 text-green-500" /> Top Gainers
                  </CardTitle>
                  <CardDescription>Stocks with the highest percentage gains today</CardDescription>
                </CardHeader>
                <CardContent>
                  {trending?.top_gainers?.length ? (
                    <div className="space-y-4">
                      {trending.top_gainers.slice(0, 10).map((stock, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-4">
                            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-bold text-green-600">{index + 1}</span>
                            </div>
                            <div>
                              <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                              <p className="text-sm text-gray-600">{stock.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(stock.current_price)}</div>
                            <div className="text-green-600 font-medium flex items-center">
                              <TrendingUp className="h-3 w-3 mr-1" /> {formatPercentage(stock.change_percent)}
                            </div>
                          </div>
                          <div className="text-right text-sm text-gray-600">
                            <div>{formatVolume(stock.volume)}</div>
                            <div>Volume</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No gainer data available</p>
                      <Button variant="outline" size="sm" className="mt-3" onClick={handleRefresh}>Retry</Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="losers">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingDown className="h-5 w-5 mr-2 text-red-500" /> Top Losers
                  </CardTitle>
                  <CardDescription>Stocks with the highest percentage losses today</CardDescription>
                </CardHeader>
                <CardContent>
                  {trending?.top_losers?.length ? (
                    <div className="space-y-4">
                      {trending.top_losers.slice(0, 10).map((stock, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-4">
                            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-bold text-red-600">{index + 1}</span>
                            </div>
                            <div>
                              <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                              <p className="text-sm text-gray-600">{stock.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(stock.current_price)}</div>
                            <div className="text-red-600 font-medium flex items-center">
                              <TrendingDown className="h-3 w-3 mr-1" /> {formatPercentage(stock.change_percent)}
                            </div>
                          </div>
                          <div className="text-right text-sm text-gray-600">
                            <div>{formatVolume(stock.volume)}</div>
                            <div>Volume</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <TrendingDown className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No loser data available</p>
                      <Button variant="outline" size="sm" className="mt-3" onClick={handleRefresh}>Retry</Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="active">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Activity className="h-5 w-5 mr-2 text-blue-500" /> Most Active
                  </CardTitle>
                  <CardDescription>Stocks with the highest trading volume today</CardDescription>
                </CardHeader>
                <CardContent>
                  {trending?.most_active?.length ? (
                    <div className="space-y-4">
                      {trending.most_active.slice(0, 10).map((stock, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-4">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                            </div>
                            <div>
                              <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
                              <p className="text-sm text-gray-600">{stock.name}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(stock.current_price)}</div>
                            <div className={`${(stock.change_percent ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'} font-medium flex items-center`}>
                              {(stock.change_percent ?? 0) >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                              {formatPercentage(stock.change_percent ?? 0)}
                            </div>
                          </div>
                          <div className="text-right text-sm text-gray-600">
                            <div className="font-bold">{formatVolume(stock.volume)}</div>
                            <div>Volume</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>No volume data available</p>
                      <Button variant="outline" size="sm" className="mt-3" onClick={handleRefresh}>Retry</Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

          </div>
        </Tabs>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Market data may be delayed. Last refreshed: {new Date().toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );
};

export default Markets;