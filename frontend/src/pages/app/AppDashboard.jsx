import React, { useState, useEffect } from "react";
import { getMarketStatsSafe, getTrendingSafe, getUsageSummary, getPortfolioValue, getAlertsUnreadCount } from "../../api/client";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Progress } from "../../components/ui/progress";
import { Link } from "react-router-dom";
import { 
  TrendingUp, 
  BarChart3, 
  Bell, 
  Search,
  Filter,
  PieChart,
  Bookmark,
  AlertTriangle,
  Newspaper,
  Activity,
  Clock,
  Zap,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Eye,
  Target
} from "lucide-react";

const AppDashboard = () => {
  const [usageData, setUsageData] = useState({
    plan: "-",
    apiCalls: { used: 0, limit: 100, hourlyUsed: 0, hourlyLimit: 0, dailyUsed: 0, dailyLimit: 0 },
    alerts: { active: 0, triggered: 0 },
    portfolio: { value: 0, change: 0, changePercent: 0 }
  });

  const [marketOverview, setMarketOverview] = useState({ gainers: 0, losers: 0, unchanged: 0, volume: "-" });
  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, trendingRes, usageRes, portfolioRes, unreadRes] = await Promise.all([
          getMarketStatsSafe().catch(() => ({ success: false })),
          getTrendingSafe().catch(() => ({ success: false })),
          getUsageSummary().catch(() => null),
          getPortfolioValue().catch(() => null),
          getAlertsUnreadCount().catch(() => ({ count: 0 }))
        ]);

        if (statsRes?.success && statsRes.data?.market_overview) {
          const mo = statsRes.data.market_overview;
          setMarketOverview({
            gainers: Number(mo.gainers || 0),
            losers: Number(mo.losers || 0),
            unchanged: Number(mo.unchanged || 0),
            volume: "—"
          });
        }

        const plan = (usageRes?.data?.account?.plan_type || usageRes?.data?.plan_type || "-").toString().replace(/^./, c => c.toUpperCase());
        const usedMonthly = Number(usageRes?.data?.monthly?.api_calls || 0);
        const limit = Number(usageRes?.data?.monthly?.limit || 100);
        const portfolioValue = Number(portfolioRes?.total_value || portfolioRes?.data?.total_value || 0);
        const activeAlerts = Number(unreadRes?.count || 0);

        setUsageData((prev) => ({
          plan: plan || prev.plan,
          apiCalls: { used: usedMonthly, limit, hourlyUsed: prev.apiCalls.hourlyUsed, hourlyLimit: prev.apiCalls.hourlyLimit, dailyUsed: prev.apiCalls.dailyUsed, dailyLimit: prev.apiCalls.dailyLimit },
          alerts: { active: activeAlerts, triggered: prev.alerts.triggered },
          portfolio: { value: portfolioValue, change: prev.portfolio.change, changePercent: prev.portfolio.changePercent }
        }));
      } catch {}
    };
    load();
  }, []);

  const quickLinks = [
    {
      title: "Stock Screener",
      description: "Find trading opportunities",
      icon: <Filter className="h-6 w-6" />,
      href: "/app/screeners",
      color: "bg-blue-600"
    },
    {
      title: "Portfolio",
      description: "Track your positions",
      icon: <PieChart className="h-6 w-6" />,
      href: "/app/portfolio", 
      color: "bg-green-600"
    },
    {
      title: "Watchlists",
      description: "Monitor favorites",
      icon: <Bookmark className="h-6 w-6" />,
      href: "/app/watchlists",
      color: "bg-purple-600"
    },
    {
      title: "Alerts",
      description: "Manage notifications",
      icon: <Bell className="h-6 w-6" />,
      href: "/app/alerts",
      color: "bg-orange-600"
    },
    {
      title: "Market News",
      description: "Stay informed",
      icon: <Newspaper className="h-6 w-6" />,
      href: "/app/news",
      color: "bg-red-600"
    },
    {
      title: "Stock Search",
      description: "Look up any stock",
      icon: <Search className="h-6 w-6" />,
      href: "/app/stocks",
      color: "bg-indigo-600"
    }
  ];

  const recentAlerts = [
    {
      symbol: "AAPL",
      message: "Price crossed above $180.00",
      time: "5 min ago",
      type: "price"
    },
    {
      symbol: "TSLA",
      message: "Volume spike detected (+150%)",
      time: "12 min ago", 
      type: "volume"
    },
    {
      symbol: "MSFT",
      message: "Earnings announcement tomorrow",
      time: "1 hour ago",
      type: "news"
    }
  ];

  const topMovers = [
    { symbol: "NVDA", price: "$425.30", change: "+12.50", changePercent: "+3.02%" },
    { symbol: "AMD", price: "$142.80", change: "+8.20", changePercent: "+6.10%" },
    { symbol: "INTC", price: "$28.45", change: "-1.25", changePercent: "-4.20%" }
  ];

  const getUsageColor = (used, limit) => {
    const percentage = (used / limit) * 100;
    if (percentage >= 90) return "text-red-600";
    if (percentage >= 75) return "text-yellow-600";
    return "text-green-600";
  };

  const getUsageProgress = (used, limit) => {
    return Math.min((used / limit) * 100, 100);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-xl text-gray-600">Welcome back! Here's your trading overview.</p>
          <div className="mt-3 flex gap-2">
            <Button asChild size="sm"><Link to="/app/screeners/new"><Filter className="h-4 w-4 mr-1"/>Create Screener</Link></Button>
            <Button asChild size="sm" variant="outline"><Link to="/app/screeners"><Search className="h-4 w-4 mr-1"/>Your Screeners</Link></Button>
          </div>
        </div>

        {/* Usage Overview */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center justify-between">
                API Usage - Monthly
                <Badge variant="secondary">{usageData.plan} Plan</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Used this month</span>
                  <span className={getUsageColor(usageData.apiCalls.used, usageData.apiCalls.limit)}>
                    {usageData.apiCalls.used.toLocaleString()} / {usageData.apiCalls.limit.toLocaleString()}
                  </span>
                </div>
                <Progress 
                  value={getUsageProgress(usageData.apiCalls.used, usageData.apiCalls.limit)} 
                  className="h-2"
                />
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Hourly:</span>
                    <span className={`ml-2 ${getUsageColor(usageData.apiCalls.hourlyUsed, usageData.apiCalls.hourlyLimit)}`}>
                      {usageData.apiCalls.hourlyUsed}/{usageData.apiCalls.hourlyLimit}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Daily:</span>
                    <span className={`ml-2 ${getUsageColor(usageData.apiCalls.dailyUsed, usageData.apiCalls.dailyLimit)}`}>
                      {usageData.apiCalls.dailyUsed}/{usageData.apiCalls.dailyLimit}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <Bell className="h-5 w-5 mr-2" />
                Alerts Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Active Alerts</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {usageData.alerts.active}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Triggered Today</span>
                  <span className="text-2xl font-bold text-green-600">
                    {usageData.alerts.triggered}
                  </span>
                </div>
                <Button asChild size="sm" className="w-full">
                  <Link to="/app/alerts">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Alert
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Portfolio Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-900">
                    ${usageData.portfolio.value.toLocaleString()}
                  </div>
                  <div className={`flex items-center justify-center ${
                    usageData.portfolio.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {usageData.portfolio.change >= 0 ? (
                      <ArrowUpRight className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 mr-1" />
                    )}
                    <span>
                      ${Math.abs(usageData.portfolio.change).toLocaleString()} 
                      ({usageData.portfolio.changePercent}%)
                    </span>
                  </div>
                </div>
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link to="/app/portfolio">
                    <Eye className="h-4 w-4 mr-2" />
                    View Details
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Links */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickLinks.map((link, index) => (
              <Link key={index} to={link.href}>
                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 ${link.color} rounded-lg flex items-center justify-center text-white`}>
                        {link.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{link.title}</h3>
                        <p className="text-sm text-gray-600">{link.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Market Overview & Recent Activity */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Market Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                Market Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <ArrowUpRight className="h-6 w-6 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-600">{marketOverview.gainers}</div>
                  <div className="text-sm text-gray-600">Gainers</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <ArrowDownRight className="h-6 w-6 text-red-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-red-600">{marketOverview.losers}</div>
                  <div className="text-sm text-gray-600">Losers</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Activity className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-gray-600">{marketOverview.unchanged}</div>
                  <div className="text-sm text-gray-600">Unchanged</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-600">{marketOverview.volume}</div>
                  <div className="text-sm text-gray-600">Volume</div>
                </div>
              </div>
              <Button asChild variant="outline" className="w-full mt-4">
                <Link to="/app/markets">
                  View Full Market Data
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Recent Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Recent Alerts
                </div>
                <Badge variant="secondary">{recentAlerts.length} Active</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentAlerts.map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant="outline" className="text-xs">{alert.symbol}</Badge>
                        <span className="text-xs text-gray-500">{alert.time}</span>
                      </div>
                      <p className="text-sm text-gray-900">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </div>
              <Button asChild variant="outline" className="w-full mt-4">
                <Link to="/app/alerts">
                  View All Alerts
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Top Movers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Top Movers Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {topMovers.map((stock, index) => (
                <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex justify-between items-center mb-2">
                    <Badge variant="outline">{stock.symbol}</Badge>
                    <span className="text-lg font-semibold">{stock.price}</span>
                  </div>
                  <div className={`flex items-center ${
                    stock.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stock.change.startsWith('+') ? (
                      <ArrowUpRight className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 mr-1" />
                    )}
                    <span className="text-sm font-medium">
                      {stock.change} ({stock.changePercent})
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <Button asChild variant="outline" className="w-full mt-4">
              <Link to="/app/stocks">
                <Target className="h-4 w-4 mr-2" />
                Explore More Stocks
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Upgrade CTA for Free/Low-tier users */}
        {usageData.plan !== "Gold" && (
          <Card className="mt-8 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <CardContent className="p-8 text-center">
              <Zap className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">Unlock More Features</h3>
              <p className="text-blue-100 mb-6">
                Upgrade to get unlimited API calls, advanced alerts, and priority support.
              </p>
              <Button asChild variant="secondary" size="lg">
                <Link to="/pricing">
                  Upgrade Plan
                  <ArrowUpRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AppDashboard;