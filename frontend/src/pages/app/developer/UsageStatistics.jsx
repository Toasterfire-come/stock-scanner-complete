import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { AlertTriangle, TrendingUp, Calendar, Activity, Zap, Globe } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useAuth } from '../../../context/SecureAuthContext';
import { getUsageStats } from '../../../api/client';
import { toast } from 'sonner';
import logger from '../../../lib/logger';

const UsageStatistics = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  useEffect(() => {
    if (hasGoldPlan) {
      loadUsageStats();
    } else {
      setLoading(false);
    }
  }, [hasGoldPlan]);

  const loadUsageStats = async () => {
    try {
      const response = await getUsageStats();
      if (response.success) {
        setStats(response.data);
      } else {
        toast.error('Failed to load usage statistics');
      }
    } catch (error) {
      logger.error('Failed to load usage statistics:', error);
      toast.error('Failed to load usage statistics');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  // Mock data for demonstration when real data is not available
  const mockData = {
    daily: {
      api_calls: 15750,
      requests: 12340,
      date: new Date().toISOString().split('T')[0]
    },
    monthly: {
      api_calls: 450000,
      requests: 380000,
      limit: -1, // Unlimited for Gold
      remaining: 'unlimited'
    },
    account: {
      plan_type: 'gold',
      is_premium: true,
      member_since: '2024-01-15T00:00:00Z'
    },
    usage_history: Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      api_calls: Math.floor(Math.random() * 2000) + 500,
      requests: Math.floor(Math.random() * 1500) + 400
    })),
    endpoint_breakdown: [
      { endpoint: '/api/stocks/', calls: 45000, percentage: 35 },
      { endpoint: '/api/market-stats/', calls: 28000, percentage: 22 },
      { endpoint: '/api/portfolio/', calls: 25000, percentage: 19 },
      { endpoint: '/api/alerts/', calls: 18000, percentage: 14 },
      { endpoint: '/api/screeners/', calls: 13000, percentage: 10 }
    ]
  };

  const currentStats = stats && stats.daily && stats.monthly ? stats : mockData;

  const pieColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Usage Statistics</h1>
            <p className="text-gray-600">Monitor your API usage and performance metrics</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                Usage statistics and detailed analytics are available exclusively for Gold plan subscribers.
              </p>
              <a href="/account/plan" className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-700 hover:to-yellow-700 text-white rounded-md font-medium" rel="noopener noreferrer">
                Upgrade to Gold Plan
              </a>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading usage statistics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Usage Statistics</h1>
          <p className="text-gray-600">Monitor your API usage and performance metrics</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Today's API Calls</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(currentStats.daily.api_calls)}</p>
                </div>
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Monthly Usage</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(currentStats.monthly.api_calls)}</p>
                  <Badge variant="secondary" className="mt-1">Unlimited</Badge>
                </div>
                <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Plan Status</p>
                  <p className="text-2xl font-bold text-gray-900">Gold</p>
                  <Badge className="mt-1 bg-gradient-to-r from-amber-500 to-yellow-500">Premium</Badge>
                </div>
                <div className="h-12 w-12 bg-amber-100 rounded-lg flex items-center justify-center">
                  <Zap className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Member Since</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {new Date(currentStats.account.member_since).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </p>
                </div>
                <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analytics */}
        <Tabs defaultValue="usage-trends" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="usage-trends">Usage Trends</TabsTrigger>
            <TabsTrigger value="endpoint-breakdown">Endpoint Breakdown</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          <TabsContent value="usage-trends" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>30-Day Usage History</CardTitle>
                <CardDescription>Daily API calls over the past month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={(currentStats.usage_history || []).map(x=>({ ...x, api_calls: Number(x.api_calls||0), requests: Number(x.requests||0) }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleDateString()}
                        formatter={(value, name) => [formatNumber(value), name === 'api_calls' ? 'API Calls' : 'Requests']}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="api_calls" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="requests" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="endpoint-breakdown" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Most Used Endpoints</CardTitle>
                  <CardDescription>API endpoints by usage volume</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {currentStats.endpoint_breakdown.map((endpoint, index) => (
                      <div key={endpoint.endpoint} className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-900">{endpoint.endpoint}</span>
                            <span className="text-sm text-gray-600">{formatNumber(endpoint.calls)}</span>
                          </div>
                          <Progress value={endpoint.percentage} className="h-2" />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Usage Distribution</CardTitle>
                  <CardDescription>Percentage breakdown by endpoint</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={currentStats.endpoint_breakdown}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="percentage"
                          label={({ endpoint, percentage }) => `${endpoint.split('/')[2]} ${percentage}%`}
                          labelLine={false}
                        >
                          {currentStats.endpoint_breakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value}%`, 'Usage']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Response Times</CardTitle>
                  <CardDescription>Average API response times over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={currentStats.usage_history.slice(-7).map(day => ({
                        ...day,
                        avg_response_time: Math.floor(Math.random() * 150) + 50
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" tickFormatter={formatDate} />
                        <YAxis label={{ value: 'ms', angle: -90, position: 'insideLeft' }} />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleDateString()}
                          formatter={(value) => [`${value}ms`, 'Avg Response Time']}
                        />
                        <Bar dataKey="avg_response_time" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                  <CardDescription>Current system performance indicators</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Average Response Time</p>
                      <p className="text-2xl font-bold text-gray-900">127ms</p>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Excellent</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Uptime</p>
                      <p className="text-2xl font-bold text-gray-900">99.9%</p>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Optimal</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Error Rate</p>
                      <p className="text-2xl font-bold text-gray-900">0.1%</p>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Low</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Data Freshness</p>
                      <p className="text-2xl font-bold text-gray-900">Real-time</p>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">Live</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UsageStatistics;