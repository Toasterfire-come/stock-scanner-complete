import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Progress } from "./ui/progress";
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Activity,
  PieChart as PieChartIcon,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Download
} from "lucide-react";
import { getRevenueAnalytics, getPortfolio, getMarketStats } from "../api/client";

const AdvancedAnalytics = ({ userId }) => {
  const [timeframe, setTimeframe] = useState("1M");
  const [analyticsData, setAnalyticsData] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      setIsLoading(true);
      try {
        const [analytics, portfolio, market] = await Promise.all([
          getRevenueAnalytics(),
          getPortfolio(),
          getMarketStats()
        ]);
        
        setAnalyticsData(analytics);
        setPortfolioData(portfolio);
        setMarketData(market);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [timeframe]);

  // Mock data for demonstration (replace with real data from your API)
  const performanceData = [
    { date: "2024-01", portfolio: 95000, benchmark: 90000, returns: 5.5 },
    { date: "2024-02", portfolio: 102000, benchmark: 93000, returns: 7.3 },
    { date: "2024-03", portfolio: 98000, benchmark: 91000, returns: -3.9 },
    { date: "2024-04", portfolio: 106000, benchmark: 95000, returns: 8.2 },
    { date: "2024-05", portfolio: 112000, benchmark: 98000, returns: 5.7 },
    { date: "2024-06", portfolio: 118000, benchmark: 101000, returns: 5.4 }
  ];

  const sectorAllocation = [
    { name: "Technology", value: 35, color: "#0088FE" },
    { name: "Healthcare", value: 20, color: "#00C49F" },
    { name: "Finance", value: 15, color: "#FFBB28" },
    { name: "Consumer", value: 12, color: "#FF8042" },
    { name: "Energy", value: 10, color: "#8884D8" },
    { name: "Other", value: 8, color: "#82CA9D" }
  ];

  const riskMetrics = {
    sharpeRatio: 1.42,
    beta: 0.95,
    volatility: 18.5,
    maxDrawdown: -12.3,
    var95: -4.2,
    tracking_error: 3.1
  };

  const topHoldings = [
    { symbol: "AAPL", weight: 8.5, value: 95400, change: 2.3 },
    { symbol: "MSFT", weight: 7.2, value: 80640, change: 1.8 },
    { symbol: "NVDA", weight: 6.8, value: 76160, change: 4.1 },
    { symbol: "GOOGL", weight: 5.9, value: 66080, change: -0.7 },
    { symbol: "TSLA", weight: 4.8, value: 53760, change: 3.2 }
  ];

  const alertsData = [
    { type: "Price Alert", count: 12, triggered: 3, color: "bg-blue-500" },
    { type: "Volume Alert", count: 8, triggered: 2, color: "bg-green-500" },
    { type: "News Alert", count: 15, triggered: 7, color: "bg-yellow-500" },
    { type: "Technical Alert", count: 6, triggered: 1, color: "bg-purple-500" }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Portfolio Analytics</h2>
          <p className="text-gray-600">Institutional-grade performance analysis</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1W">1 Week</SelectItem>
              <SelectItem value="1M">1 Month</SelectItem>
              <SelectItem value="3M">3 Months</SelectItem>
              <SelectItem value="6M">6 Months</SelectItem>
              <SelectItem value="1Y">1 Year</SelectItem>
              <SelectItem value="ALL">All Time</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Return</p>
                <p className="text-2xl font-bold text-green-600">+18.7%</p>
                <p className="text-xs text-gray-500">vs S&P 500: +12.4%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                <p className="text-2xl font-bold text-blue-600">{riskMetrics.sharpeRatio}</p>
                <p className="text-xs text-gray-500">Risk-adjusted returns</p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Max Drawdown</p>
                <p className="text-2xl font-bold text-red-600">{riskMetrics.maxDrawdown}%</p>
                <p className="text-xs text-gray-500">Peak-to-trough decline</p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Portfolio Beta</p>
                <p className="text-2xl font-bold text-purple-600">{riskMetrics.beta}</p>
                <p className="text-xs text-gray-500">Market sensitivity</p>
              </div>
              <Activity className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="performance" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="allocation">Allocation</TabsTrigger>
          <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          {/* Performance Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Performance vs Benchmark</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [`$${value.toLocaleString()}`, name]} />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="portfolio" 
                    stroke="#2563eb" 
                    fill="#3b82f6" 
                    fillOpacity={0.3}
                    name="Portfolio Value"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="benchmark" 
                    stroke="#059669" 
                    fill="#10b981" 
                    fillOpacity={0.3}
                    name="S&P 500"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Top Holdings */}
          <Card>
            <CardHeader>
              <CardTitle>Top Holdings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topHoldings.map((holding, index) => (
                  <div key={holding.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">{holding.symbol}</Badge>
                      <div>
                        <p className="font-medium">{holding.weight}% allocation</p>
                        <p className="text-sm text-gray-600">${holding.value.toLocaleString()}</p>
                      </div>
                    </div>
                    <div className={`flex items-center ${holding.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {holding.change >= 0 ? (
                        <ArrowUpRight className="h-4 w-4 mr-1" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 mr-1" />
                      )}
                      <span className="font-medium">{Math.abs(holding.change)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="allocation" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Sector Allocation Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Sector Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sectorAllocation}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {sectorAllocation.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Allocation Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Asset Allocation Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sectorAllocation.map((sector, index) => (
                    <div key={sector.name} className="space-y-2">
                      <div className="flex justify-between">
                        <span className="font-medium">{sector.name}</span>
                        <span>{sector.value}%</span>
                      </div>
                      <Progress value={sector.value} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="risk" className="space-y-6">
          {/* Risk Metrics */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <h3 className="font-semibold text-gray-600">Volatility</h3>
                <p className="text-3xl font-bold text-orange-600">{riskMetrics.volatility}%</p>
                <p className="text-sm text-gray-500">Annual standard deviation</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <h3 className="font-semibold text-gray-600">Value at Risk (95%)</h3>
                <p className="text-3xl font-bold text-red-600">{riskMetrics.var95}%</p>
                <p className="text-sm text-gray-500">Daily potential loss</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <h3 className="font-semibold text-gray-600">Tracking Error</h3>
                <p className="text-3xl font-bold text-purple-600">{riskMetrics.tracking_error}%</p>
                <p className="text-sm text-gray-500">vs benchmark deviation</p>
              </CardContent>
            </Card>
          </div>

          {/* Risk-Return Scatter Plot */}
          <Card>
            <CardHeader>
              <CardTitle>Risk-Return Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="returns" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Monthly Returns %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          {/* Alert Summary */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {alertsData.map((alert, index) => (
              <Card key={alert.type}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{alert.type}</p>
                      <p className="text-2xl font-bold">{alert.count}</p>
                      <p className="text-xs text-gray-500">{alert.triggered} triggered today</p>
                    </div>
                    <div className={`w-12 h-12 ${alert.color} rounded-full flex items-center justify-center`}>
                      <span className="text-white font-bold">{alert.triggered}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Alert Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Alert Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={alertsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" name="Total Alerts" />
                  <Bar dataKey="triggered" fill="#ef4444" name="Triggered" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Alert Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Optimization Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-blue-900">Price Alert Optimization</p>
                    <p className="text-sm text-blue-700">Consider reducing price alert sensitivity by 2% to reduce noise while maintaining effectiveness.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-4 bg-yellow-50 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-900">Volume Alert Gap</p>
                    <p className="text-sm text-yellow-700">Add volume alerts for TSLA and NVDA to catch momentum changes earlier.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-green-900">News Alert Success</p>
                    <p className="text-sm text-green-700">Your news alerts have a 78% accuracy rate for predicting significant moves.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalytics;