import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import DashboardCustomizer from "../../components/DashboardCustomizer";
import { 
  AnimatedCard, 
  AnimatedCounter, 
  AnimatedProgress, 
  StaggeredList,
  AnimatedPrice,
  SkeletonLoader
} from "../../components/AnimatedComponents";
import {
import logger from '../../lib/logger';
  TrendingUp,
  TrendingDown,
  BarChart3,
  DollarSign,
  Target,
  Eye,
  Bell,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Clock,
  AlertCircle
} from "lucide-react";

const EnhancedDashboard = () => {
  const [dashboardLayout, setDashboardLayout] = useState([]);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulated market data
  const mockMarketData = {
    indices: [
      { symbol: "SPY", name: "S&P 500", price: 521.45, change: 12.34, changePercent: 2.43 },
      { symbol: "QQQ", name: "NASDAQ", price: 378.92, change: -5.67, changePercent: -1.47 },
      { symbol: "DIA", name: "Dow Jones", price: 394.28, change: 8.91, changePercent: 2.31 }
    ],
    portfolio: {
      totalValue: 145750.25,
      dayChange: 2847.83,
      dayChangePercent: 1.99,
      positions: 12
    },
    alerts: [
      { id: 1, symbol: "AAPL", message: "Price above $180", time: "2 mins ago", type: "price" },
      { id: 2, symbol: "TSLA", message: "Volume spike detected", time: "5 mins ago", type: "volume" },
      { id: 3, symbol: "MSFT", message: "Earnings announcement", time: "1 hour ago", type: "news" }
    ],
    topMovers: {
      gainers: [
        { symbol: "NVDA", change: 8.45, changePercent: 12.34 },
        { symbol: "AMD", change: 4.23, changePercent: 8.91 },
        { symbol: "TSLA", change: 15.67, changePercent: 7.89 }
      ],
      losers: [
        { symbol: "META", change: -12.34, changePercent: -4.56 },
        { symbol: "NFLX", change: -8.91, changePercent: -3.21 },
        { symbol: "GOOGL", change: -5.67, changePercent: -2.45 }
      ]
    }
  };

  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setMarketData(mockMarketData);
      setLoading(false);
    }, 1500);

    // Load saved layout
    const savedLayout = localStorage.getItem('dashboard-layout');
    if (savedLayout) {
      try {
        setDashboardLayout(JSON.parse(savedLayout));
      } catch (e) {
        logger.error('Failed to parse saved layout:', e);
      }
    }

    return () => clearTimeout(timer);
  }, []);

  const handleLayoutChange = (newLayout) => {
    setDashboardLayout(newLayout);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50/30 to-indigo-100/30 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <SkeletonLoader width="200px" height="32px" />
            <SkeletonLoader width="150px" height="40px" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6 space-y-4">
                  <SkeletonLoader width="100%" height="20px" />
                  <SkeletonLoader width="60%" height="32px" />
                  <SkeletonLoader width="80%" height="16px" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const WidgetComponents = {
    'market-overview': (
      <AnimatedCard key="market-overview" className="col-span-full lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Market Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {marketData.indices.map((index, i) => (
              <div key={index.symbol} className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">
                  {index.name}
                </div>
                <AnimatedPrice 
                  price={index.price}
                  change={index.change}
                  changePercent={index.changePercent}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </AnimatedCard>
    ),

    'portfolio-summary': (
      <AnimatedCard key="portfolio-summary" className="col-span-full lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-green-600" />
            Portfolio Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <div className="text-3xl font-bold">
                $<AnimatedCounter value={marketData.portfolio.totalValue} decimals={2} />
              </div>
              <div className={`flex items-center gap-1 text-sm ${
                marketData.portfolio.dayChange >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {marketData.portfolio.dayChange >= 0 ? 
                  <ArrowUpRight className="h-4 w-4" /> : 
                  <ArrowDownRight className="h-4 w-4" />
                }
                <AnimatedCounter 
                  value={Math.abs(marketData.portfolio.dayChange)} 
                  prefix={marketData.portfolio.dayChange >= 0 ? '+$' : '-$'}
                  decimals={2}
                />
                <span>
                  ({marketData.portfolio.dayChange >= 0 ? '+' : ''}
                  <AnimatedCounter value={marketData.portfolio.dayChangePercent} decimals={2} />%)
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{marketData.portfolio.positions} positions</span>
              <Badge variant="outline">
                <Activity className="h-3 w-3 mr-1" />
                Active
              </Badge>
            </div>
          </div>
        </CardContent>
      </AnimatedCard>
    ),

    'recent-alerts': (
      <AnimatedCard key="recent-alerts">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-orange-600" />
            Recent Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <StaggeredList className="space-y-3">
            {marketData.alerts.map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                <AlertCircle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{alert.symbol}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {alert.message}
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <Clock className="h-3 w-3" />
                    {alert.time}
                  </div>
                </div>
              </div>
            ))}
          </StaggeredList>
        </CardContent>
      </AnimatedCard>
    ),

    'top-movers': (
      <AnimatedCard key="top-movers">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-purple-600" />
            Top Movers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-green-600 mb-2">Top Gainers</h4>
              <div className="space-y-2">
                {marketData.topMovers.gainers.map((stock) => (
                  <div key={stock.symbol} className="flex items-center justify-between">
                    <span className="font-medium text-sm">{stock.symbol}</span>
                    <div className="flex items-center gap-1 text-green-600 text-sm">
                      <TrendingUp className="h-3 w-3" />
                      +{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-red-600 mb-2">Top Losers</h4>
              <div className="space-y-2">
                {marketData.topMovers.losers.map((stock) => (
                  <div key={stock.symbol} className="flex items-center justify-between">
                    <span className="font-medium text-sm">{stock.symbol}</span>
                    <div className="flex items-center gap-1 text-red-600 text-sm">
                      <TrendingDown className="h-3 w-3" />
                      {stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </AnimatedCard>
    ),

    'quick-actions': (
      <AnimatedCard key="quick-actions">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-600" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2">
            <Button variant="outline" size="sm" className="flex flex-col h-auto p-3">
              <BarChart3 className="h-4 w-4 mb-1" />
              <span className="text-xs">New Screener</span>
            </Button>
            <Button variant="outline" size="sm" className="flex flex-col h-auto p-3">
              <Bell className="h-4 w-4 mb-1" />
              <span className="text-xs">Set Alert</span>
            </Button>
            <Button variant="outline" size="sm" className="flex flex-col h-auto p-3">
              <Eye className="h-4 w-4 mb-1" />
              <span className="text-xs">Watchlist</span>
            </Button>
            <Button variant="outline" size="sm" className="flex flex-col h-auto p-3">
              <Target className="h-4 w-4 mb-1" />
              <span className="text-xs">Portfolio</span>
            </Button>
          </div>
        </CardContent>
      </AnimatedCard>
    )
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/30 to-indigo-100/30 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back! Here's what's happening in your portfolio.
            </p>
          </div>
          <DashboardCustomizer 
            currentLayout={dashboardLayout}
            onLayoutChange={handleLayoutChange}
          />
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <AnimatedCard>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Value</p>
                  <p className="text-2xl font-bold">
                    $<AnimatedCounter value={145750} />
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </AnimatedCard>

          <AnimatedCard>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Day Change</p>
                  <p className="text-2xl font-bold text-green-600">
                    +$<AnimatedCounter value={2847} />
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </AnimatedCard>

          <AnimatedCard>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Alerts</p>
                  <p className="text-2xl font-bold">
                    <AnimatedCounter value={7} />
                  </p>
                </div>
                <Bell className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </AnimatedCard>

          <AnimatedCard>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Watchlist Items</p>
                  <p className="text-2xl font-bold">
                    <AnimatedCounter value={23} />
                  </p>
                </div>
                <Eye className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </AnimatedCard>
        </div>

        {/* Dynamic Widget Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {dashboardLayout.length > 0 ? (
            dashboardLayout.map((widget) => {
              const widgetId = widget.id || widget;
              return WidgetComponents[widgetId] || null;
            })
          ) : (
            // Default layout if no customization
            <>
              {WidgetComponents['market-overview']}
              {WidgetComponents['portfolio-summary']}
              {WidgetComponents['recent-alerts']}
              {WidgetComponents['top-movers']}
              {WidgetComponents['quick-actions']}
            </>
          )}
        </div>

        {/* Progress Indicator */}
        <AnimatedCard>
          <CardHeader>
            <CardTitle>Account Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">API Calls Used</span>
                  <span className="text-sm font-medium">
                    <AnimatedCounter value={847} /> / 1,500
                  </span>
                </div>
                <AnimatedProgress value={847} max={1500} />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm">Storage Used</span>
                  <span className="text-sm font-medium">
                    <AnimatedCounter value={2.4} decimals={1} />GB / 5GB
                  </span>
                </div>
                <AnimatedProgress value={2.4} max={5} />
              </div>
            </div>
          </CardContent>
        </AnimatedCard>
      </div>
    </div>
  );
};

export default EnhancedDashboard;