import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3, 
  Bell,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  PieChart,
  AlertTriangle,
  Clock,
  Star
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { getMarketStats, getTrending, getPortfolio, getWatchlist } from "../../api/client";

const AppDashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [marketStats, setMarketStats] = useState(null);
  const [trending, setTrending] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [watchlist, setWatchlist] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsResponse, trendingResponse, portfolioResponse, watchlistResponse] = await Promise.all([
          getMarketStats().catch(() => null),
          getTrending().catch(() => null),
          getPortfolio().catch(() => null),
          getWatchlist().catch(() => null)
        ]);

        setMarketStats(statsResponse);
        setTrending(trendingResponse);
        setPortfolio(portfolioResponse);
        setWatchlist(watchlistResponse);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-64" />
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
                  {[1, 2, 3].map((i) => (
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
                  {[1, 2, 3].map((i) => (
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
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.first_name || user?.username}
            </h1>
            <p className="text-gray-600 mt-2">
              Here's what's happening in the markets today
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button asChild>
              <Link to="/app/screeners/new">
                <Plus className="h-4 w-4 mr-2" />
                New Screen
              </Link>
            </Button>
          </div>
        </div>

        {/* Market Overview */}
        {marketStats && (
          <div className="grid md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Stocks</p>
                    <p className="text-2xl font-bold">
                      {marketStats.market_overview.total_stocks.toLocaleString()}
                    </p>
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
                      <p className="text-2xl font-bold text-green-600">
                        {marketStats.market_overview.gainers.toLocaleString()}
                      </p>
                      <TrendingUp className="h-5 w-5 text-green-500 ml-2" />
                    </div>
                  </div>
                  <ArrowUpRight className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Losers</p>
                    <div className="flex items-center">
                      <p className="text-2xl font-bold text-red-600">
                        {marketStats.market_overview.losers.toLocaleString()}
                      </p>
                      <TrendingDown className="h-5 w-5 text-red-500 ml-2" />
                    </div>
                  </div>
                  <ArrowDownRight className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Unchanged</p>
                    <p className="text-2xl font-bold text-gray-600">
                      {marketStats.market_overview.unchanged.toLocaleString()}
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-gray-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Portfolio Summary */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Portfolio Summary
              </CardTitle>
              <Button asChild variant="ghost" size="sm">
                <Link to="/app/portfolio">
                  View All
                  <ArrowUpRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {portfolio?.data?.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-blue-600">Total Value</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {formatCurrency(portfolio.summary.total_value)}
                      </p>
                    </div>
                    <div className={`p-4 rounded-lg ${
                      portfolio.summary.total_gain_loss >= 0 ? 'bg-green-50' : 'bg-red-50'
                    }`}>
                      <p className={`text-sm ${
                        portfolio.summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        Total P&L
                      </p>
                      <p className={`text-2xl font-bold ${
                        portfolio.summary.total_gain_loss >= 0 ? 'text-green-900' : 'text-red-900'
                      }`}>
                        {formatCurrency(portfolio.summary.total_gain_loss)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {portfolio.data.slice(0, 3).map((holding) => (
                      <div key={holding.id} className="flex items-center justify-between">
                        <div>
                          <span className="font-medium">{holding.symbol}</span>
                          <span className="text-sm text-gray-500 ml-2">
                            {holding.shares} shares
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">
                            {formatCurrency(holding.total_value)}
                          </div>
                          <div className={`text-sm ${
                            holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercentage(holding.gain_loss_percent)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <PieChart className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Portfolio Yet</h3>
                  <p className="text-gray-600 mb-4">
                    Start tracking your investments
                  </p>
                  <Button asChild>
                    <Link to="/app/portfolio">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Holdings
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Top Gainers */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Top Gainers
              </CardTitle>
              <Button asChild variant="ghost" size="sm">
                <Link to="/app/top-movers">
                  View All
                  <ArrowUpRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {trending?.top_gainers?.length > 0 ? (
                <div className="space-y-3">
                  {trending.top_gainers.slice(0, 5).map((stock, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <Link 
                          to={`/app/stocks/${stock.ticker}`}
                          className="font-medium hover:text-blue-600"
                        >
                          {stock.ticker}
                        </Link>
                        <p className="text-sm text-gray-500">{stock.name}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">
                          {formatCurrency(stock.current_price)}
                        </div>
                        <div className="text-sm text-green-600 flex items-center">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {formatPercentage(stock.change_percent)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <TrendingUp className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">No market data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Watchlist */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="flex items-center">
                <Star className="h-5 w-5 mr-2" />
                Watchlist
              </CardTitle>
              <Button asChild variant="ghost" size="sm">
                <Link to="/app/watchlists">
                  Manage
                  <ArrowUpRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {watchlist?.data?.length > 0 ? (
                <div className="space-y-3">
                  {watchlist.data.slice(0, 5).map((item) => (
                    <div key={item.id} className="flex items-center justify-between">
                      <div>
                        <Link 
                          to={`/app/stocks/${item.symbol}`}
                          className="font-medium hover:text-blue-600"
                        >
                          {item.symbol}
                        </Link>
                        <p className="text-sm text-gray-500">{item.company_name}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">
                          {formatCurrency(item.current_price)}
                        </div>
                        <div className={`text-sm flex items-center ${
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
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Star className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Watchlist Yet</h3>
                  <p className="text-gray-600 mb-4">
                    Start watching stocks you're interested in
                  </p>
                  <Button asChild>
                    <Link to="/app/stocks">
                      <Plus className="h-4 w-4 mr-2" />
                      Browse Stocks
                    </Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks and shortcuts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button asChild className="w-full justify-start">
                <Link to="/app/screeners/new">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Create New Screener
                </Link>
              </Button>
              
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/alerts">
                  <Bell className="h-4 w-4 mr-2" />
                  Set Price Alert
                </Link>
              </Button>
              
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/markets">
                  <Activity className="h-4 w-4 mr-2" />
                  Market Overview
                </Link>
              </Button>
              
              <Button asChild variant="outline" className="w-full justify-start">
                <Link to="/app/news">
                  <Clock className="h-4 w-4 mr-2" />
                  Latest News
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Alerts Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Recent Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Recent Alerts</h3>
              <p className="text-gray-600 mb-4">
                Set up price alerts to stay informed about your favorite stocks
              </p>
              <Button asChild>
                <Link to="/app/alerts">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Alert
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AppDashboard;