import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Link } from "react-router-dom";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  Bell,
  Eye,
  Users,
  AlertTriangle,
  ArrowRight,
  Play,
  PieChart,
  Target,
  Calendar,
  Download
} from "lucide-react";
import { useAuth } from "../../context/SecureAuthContext";
import { 
  getTrendingSafe, 
  getMarketStatsSafe, 
  getStatisticsSafe, 
  getCurrentApiUsage, 
  getPlanLimits,
  getPortfolioAnalytics,
  getUserActivityFeed,
  getMarketStatus,
  getSectorPerformance,
  API_ROOT,
  normalizeMarketStats,
  normalizeTrending
} from "../../api/client";
import MiniSparkline from "../../components/MiniSparkline";
import RealTrendingSparkline from "../../components/RealTrendingSparkline";
import UsageTracker from "../../components/UsageTracker";
import PlanUsage from "../../components/PlanUsage";
// Removed EnhancedPortfolioAnalytics and RealUserActivityFeed from dashboard per request
import MarketStatus from "../../components/MarketStatus";

const AppDashboard = () => {
  const { isAuthenticated, user } = useAuth();
  const [marketData, setMarketData] = useState(null);
  const [trendingStocks, setTrendingStocks] = useState(null);
  const [portfolioAnalytics, setPortfolioAnalytics] = useState(null);
  const [userActivity, setUserActivity] = useState([]);
  
  const [sectorPerformance, setSectorPerformance] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [usage, setUsage] = useState(null);
  const [realTrendSeries, setRealTrendSeries] = useState({ gainers: [], losers: [], total: [] });

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // Fetch all dashboard data in parallel
        const [
          marketResponse, 
          trendingResponse, 
          stats,
          portfolioResponse,
          activityResponse,
          sectorResponse
        ] = await Promise.all([
          getMarketStatsSafe(),
          getTrendingSafe(),
          getStatisticsSafe().catch(() => ({ success: false })),
          getPortfolioAnalytics().catch(() => null),
          getUserActivityFeed().catch(() => []),
          getSectorPerformance().catch(() => [])
        ]);

        // Fallback direct fetch to guarantee calls happen even if wrappers fail silently
        let marketDataResolved = marketResponse?.data;
        if (!marketDataResolved) {
          try {
            const r = await fetch(`${API_ROOT}/market-stats/`, { credentials: 'include' });
            const jd = await r.json();
            marketDataResolved = normalizeMarketStats(jd);
          } catch {}
        }

        let trendingResolved = trendingResponse?.data;
        if (!trendingResolved) {
          try {
            const r = await fetch(`${API_ROOT}/trending/`, { credentials: 'include' });
            const jd = await r.json();
            trendingResolved = normalizeTrending(jd);
          } catch {}
        }

        setMarketData(marketDataResolved || null);
        setTrendingStocks(trendingResolved || null);
        setUsage(stats?.data || null);
        setPortfolioAnalytics(portfolioResponse);
        setUserActivity(activityResponse?.slice(0, 5) || []);
        setSectorPerformance(sectorResponse?.slice(0, 6) || []);

        // Use real historical data from backend or create realistic trends
        const gainersData = marketResponse?.data?.historical_gainers || generateRealisticTrend(800, 900);
        const losersData = marketResponse?.data?.historical_losers || generateRealisticTrend(600, 700);
        const totalData = marketResponse?.data?.historical_total || generateRealisticTrend(10400, 10600);
        
        setRealTrendSeries({
          gainers: gainersData,
          losers: losersData,
          total: totalData,
        });
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated]);

  // Generate realistic trend data if backend doesn't provide historical data
  const generateRealisticTrend = (baseValue, maxValue) => {
    return Array.from({ length: 20 }, (_, i) => {
      const variance = (Math.random() - 0.5) * (maxValue - baseValue) * 0.1;
      return Math.max(baseValue, Math.min(maxValue, baseValue + variance + (Math.sin(i/3) * 20)));
    });
  };

  // Format currency
  const formatCurrency = (value) => {
    if (!value) return '$0.00';
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  // Format percentage
  const formatPercentage = (value) => {
    if (!value) return '0.00%';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Welcome Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name || 'Trader'}!
          </h1>
          <p className="text-gray-600">Here's your comprehensive trading dashboard</p>
          <div className="flex items-center gap-4 mt-3">
            <Badge variant="secondary" className="text-sm">
              {(user?.plan || 'free').toString().charAt(0).toUpperCase() + (user?.plan || 'free').toString().slice(1)} Plan
            </Badge>
            <MarketStatus />
          </div>
        </div>

        {/* Portfolio Summary (if user has portfolio data) */}
        {portfolioAnalytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
                <DollarSign className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(portfolioAnalytics.total_value)}</div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-muted-foreground">Today:</span>
                  <span className={`font-medium ${portfolioAnalytics.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(portfolioAnalytics.day_change)} ({formatPercentage(portfolioAnalytics.day_change_percent)})
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-green-50 to-green-100">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Gain/Loss</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${portfolioAnalytics.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(portfolioAnalytics.total_gain_loss)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatPercentage(portfolioAnalytics.total_gain_loss_percent)} all time
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-purple-50 to-purple-100">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">  
                <CardTitle className="text-sm font-medium">Holdings</CardTitle>
                <PieChart className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{portfolioAnalytics.holdings_count || 0}</div>
                <p className="text-xs text-muted-foreground">Stocks in portfolio</p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-r from-orange-50 to-orange-100">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Dividend Income</CardTitle>
                <Target className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(portfolioAnalytics.dividend_income || 0)}</div>
                <p className="text-xs text-muted-foreground">This year</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Market Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{marketData?.market_overview?.total_stocks?.toLocaleString() || '10,500+'}</div>
              <p className="text-xs text-muted-foreground">NYSE listings covered</p>
              <div className="mt-3">
                <RealTrendingSparkline dataType="total" color="#2563eb" width={60} height={20} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gainers</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{marketData?.market_overview?.gainers?.toLocaleString() || '-'}</div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-muted-foreground">Stocks up today</span>
              </div>
              <div className="mt-3">
                <RealTrendingSparkline dataType="gainers" color="#16a34a" width={60} height={20} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Losers</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{marketData?.market_overview?.losers?.toLocaleString() || '-'}</div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-muted-foreground">Stocks down today</span>
              </div>
              <div className="mt-3">
                <RealTrendingSparkline dataType="losers" color="#dc2626" width={60} height={20} />
              </div>
            </CardContent>
          </Card>

          <PlanUsage />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Top Gainers */}
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Top Gainers Today</CardTitle>
                <CardDescription>Best performing stocks from live market data</CardDescription>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link to="/app/markets">
                  View All <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {trendingStocks?.top_gainers ? (
                <div className="space-y-4">
                  {trendingStocks.top_gainers.slice(0, 5).map((stock, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1">
                        <div className="font-semibold">{stock.ticker}</div>
                        <div className="text-sm text-gray-600">{stock.name || 'Company Name'}</div>
                        <div className="text-sm text-gray-800 font-medium">{formatCurrency(stock.current_price)}</div>
                      </div>
                      <div className="text-right">
                        <Badge variant="secondary" className="bg-green-100 text-green-800 mb-1">
                          {formatPercentage(stock.change_percent)}
                        </Badge>
                        <div className="text-xs text-gray-600">
                          {formatCurrency(stock.price_change_today)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8 text-gray-500">
                  Loading market data...
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Access your most-used tools</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/stocks">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Stock Scanner
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/screeners">
                  <Target className="h-4 w-4 mr-2" />
                  My Screeners
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/watchlists">
                  <Eye className="h-4 w-4 mr-2" />
                  Watchlists
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/portfolio">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Portfolio
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/alerts">
                  <Bell className="h-4 w-4 mr-2" />
                  Alerts
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Activity & Market Status Grid */}  
        <div className="grid grid-cols-1 lg:grid-cols-1 gap-4 sm:gap-6 mt-4 sm:mt-6">
          {/* Market Status only */}
          <div>
            <MarketStatus />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppDashboard;