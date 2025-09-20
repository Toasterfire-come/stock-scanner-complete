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
  Play
} from "lucide-react";
import { useAuth } from "../../context/SecureAuthContext";
import { getTrendingSafe, getMarketStatsSafe, getEndpointStatus, getStatisticsSafe, getMarketStats, getCurrentApiUsage, getPlanLimits } from "../../api/client";
import MiniSparkline from "../../components/MiniSparkline";
import UsageTracker from "../../components/UsageTracker";

const AppDashboard = () => {
  const { isAuthenticated, user } = useAuth();
  const [marketData, setMarketData] = useState(null);
  const [trendingStocks, setTrendingStocks] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [usage, setUsage] = useState(null);
  const [trendSeries, setTrendSeries] = useState({ gainers: [], losers: [], total: [] });

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        const [marketResponse, trendingResponse, stats] = await Promise.all([
          getMarketStatsSafe(),
          getTrendingSafe(),
          getStatisticsSafe().catch(() => ({ success: false }))
        ]);

        setMarketData(marketResponse.data);
        setTrendingStocks(trendingResponse.data);
        setUsage(stats?.data || null);
        // derive simple spark series if backend provides history; otherwise create placeholders
        const g = (marketResponse?.data?.history?.gainers || []).slice(-20);
        const l = (marketResponse?.data?.history?.losers || []).slice(-20);
        const t = (marketResponse?.data?.history?.total_stocks || []).slice(-20);
        setTrendSeries({
          gainers: g.length ? g : Array.from({ length: 20 }, (_, i) => 800 + Math.sin(i/2) * 100),
          losers: l.length ? l : Array.from({ length: 20 }, (_, i) => 600 + Math.cos(i/2) * 90),
          total: t.length ? t : Array.from({ length: 20 }, (_, i) => 3200 + Math.sin(i/3) * 20),
        });
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated]);

  // Note: This component is now protected by ProtectedRoute, 
  // so non-authenticated users won't reach this code.
  // The ProtectedRoute component will handle the redirect/access control.

  // Authenticated user dashboard
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name || 'Trader'}!
          </h1>
          <p className="text-gray-600">Here's your trading dashboard overview</p>
          <Badge variant="secondary" className="mt-2">
            {user?.plan || 'Bronze'} Plan
          </Badge>
        </div>

        {/* Market Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{marketData?.market_overview?.total_stocks?.toLocaleString() || '-'}</div>
              <p className="text-xs text-muted-foreground">NYSE listings covered</p>
              {Array.isArray(trendSeries.total) && trendSeries.total.length > 0 && (
                <div className="mt-3">
                  <MiniSparkline data={trendSeries.total} color="#2563eb" />
                </div>
              )}
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
                <span className="text-green-600 font-medium">+{((marketData?.market_overview?.gainers_delta)||0)}%</span>
              </div>
              {Array.isArray(trendSeries.gainers) && trendSeries.gainers.length > 0 && (
                <div className="mt-3">
                  <MiniSparkline data={trendSeries.gainers} color="#16a34a" />
                </div>
              )}
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
                <span className="text-red-600 font-medium">{((marketData?.market_overview?.losers_delta)||0)}%</span>
              </div>
              {Array.isArray(trendSeries.losers) && trendSeries.losers.length > 0 && (
                <div className="mt-3">
                  <MiniSparkline data={trendSeries.losers} color="#dc2626" />
                </div>
              )}
            </CardContent>
          </Card>

          <UsageTracker />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Gainers */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Top Gainers Today</CardTitle>
              <CardDescription>Best performing stocks in your watchlist</CardDescription>
            </CardHeader>
            <CardContent>
              {trendingStocks?.top_gainers ? (
                <div className="space-y-4">
                  {trendingStocks.top_gainers.slice(0, 5).map((stock, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-semibold">{stock.ticker}</div>
                        <div className="text-sm text-gray-600">{stock.name}</div>
                      </div>
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        +{stock.change_percent?.toFixed(2)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Loading market data...</p>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and tools</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/stocks">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Stock Scanner
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/watchlists">
                  <Eye className="h-4 w-4 mr-2" />
                  My Watchlists
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

        {/* Additional Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest trading activities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-500">
                Recent alerts, screener results, and portfolio changes will appear here.
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Market Insights</CardTitle>
              <CardDescription>Today's market highlights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-500">
                Market analysis and insights based on current conditions.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AppDashboard;