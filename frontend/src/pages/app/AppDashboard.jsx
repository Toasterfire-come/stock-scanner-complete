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
import { useAuth } from "../../context/AuthContext";
import { getTrendingSafe, getMarketStatsSafe } from "../../api/client";

const AppDashboard = () => {
  const { isAuthenticated, user } = useAuth();
  const [marketData, setMarketData] = useState(null);
  const [trendingStocks, setTrendingStocks] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        if (isAuthenticated) {
          // Fetch real data for authenticated users
          const [marketResponse, trendingResponse] = await Promise.all([
            getMarketStatsSafe(),
            getTrendingSafe()
          ]);
          
          setMarketData(marketResponse.data);
          setTrendingStocks(trendingResponse.data);
        } else {
          // Show limited/mock data for non-authenticated users
          setMarketData({
            market_overview: {
              total_stocks: 3200,
              gainers: 1240,
              losers: 890,
              unchanged: 1070
            }
          });
          setTrendingStocks({
            top_gainers: [
              { ticker: "AAPL", name: "Apple Inc.", change_percent: 2.5 },
              { ticker: "MSFT", name: "Microsoft Corp.", change_percent: 1.8 },
              { ticker: "NVDA", name: "NVIDIA Corp.", change_percent: 3.2 }
            ]
          });
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Non-authenticated user warning */}
          <Alert className="mb-8 border-orange-200 bg-orange-50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-orange-800">
              <strong>Demo Mode:</strong> You're viewing limited sample data. 
              <Link to="/auth/sign-up" className="ml-2 text-blue-600 hover:underline font-medium">
                Sign up for $1 to access real-time data and full features →
              </Link>
            </AlertDescription>
          </Alert>

          {/* Dashboard content for non-authenticated users */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Trade Scan Pro Dashboard</h1>
            <p className="text-gray-600">Sample dashboard - limited functionality in demo mode</p>
          </div>

          {/* Sample Market Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3,200</div>
                <p className="text-xs text-muted-foreground">NYSE listings</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Gainers</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">1,240</div>
                <p className="text-xs text-muted-foreground">Stocks up today</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Losers</CardTitle>
                <TrendingDown className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">890</div>
                <p className="text-xs text-muted-foreground">Stocks down today</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Unchanged</CardTitle>
                <Activity className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-600">1,070</div>
                <p className="text-xs text-muted-foreground">No change</p>
              </CardContent>
            </Card>
          </div>

          {/* Call to Action */}
          <Card className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardContent className="p-8 text-center">
              <h2 className="text-2xl font-bold mb-4">Unlock Full Dashboard Features</h2>
              <p className="text-blue-100 mb-6 text-lg">
                Get real-time data, alerts, portfolio tracking, and advanced screening tools
              </p>
              <Button asChild size="lg" variant="secondary" className="text-blue-700">
                <Link to="/auth/sign-up">
                  <Play className="h-5 w-5 mr-2" />
                  Get Started for $1
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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
              <div className="text-2xl font-bold">
                {marketData?.market_overview?.total_stocks?.toLocaleString() || '3,200'}
              </div>
              <p className="text-xs text-muted-foreground">NYSE listings covered</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gainers</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {marketData?.market_overview?.gainers?.toLocaleString() || '1,240'}
              </div>
              <p className="text-xs text-muted-foreground">Stocks up today</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Losers</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {marketData?.market_overview?.losers?.toLocaleString() || '890'}
              </div>
              <p className="text-xs text-muted-foreground">Stocks down today</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">API Usage</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">156</div>
              <p className="text-xs text-muted-foreground">Calls this month</p>
            </CardContent>
          </Card>
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