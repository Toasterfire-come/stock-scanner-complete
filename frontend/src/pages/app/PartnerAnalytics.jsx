import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  MousePointerClick,
  ShoppingCart,
  Calendar,
  Download,
  RefreshCw,
  Link as LinkIcon,
  Copy,
  Check,
} from 'lucide-react';
import { toast } from 'sonner';
import { api } from '../../api/client';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import logger from '../../lib/logger';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function PartnerAnalytics() {
  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);
  const [timeseriesData, setTimeseriesData] = useState([]);
  const [dateRange, setDateRange] = useState('30d');
  const [referralCode, setReferralCode] = useState('');
  const [copiedLink, setCopiedLink] = useState(false);
  const [error, setError] = useState(null);

  // Fetch analytics data
  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      // Calculate date range
      const now = new Date();
      const fromDate = new Date();

      switch (dateRange) {
        case '7d':
          fromDate.setDate(now.getDate() - 7);
          break;
        case '30d':
          fromDate.setDate(now.getDate() - 30);
          break;
        case '90d':
          fromDate.setDate(now.getDate() - 90);
          break;
        case '1y':
          fromDate.setFullYear(now.getFullYear() - 1);
          break;
        default:
          fromDate.setDate(now.getDate() - 30);
      }

      const from = fromDate.toISOString().split('T')[0];
      const to = now.toISOString().split('T')[0];

      // Fetch summary data
      const summaryResponse = await api.get('/api/partner/analytics/summary', {
        params: { from, to }
      });

      if (summaryResponse.data.success) {
        setSummaryData(summaryResponse.data);
        setReferralCode(summaryResponse.data.code);
      } else {
        throw new Error(summaryResponse.data.error || 'Failed to load analytics');
      }

      // Fetch timeseries data
      const timeseriesResponse = await api.get('/api/partner/analytics/timeseries', {
        params: { from, to, interval: 'day' }
      });

      if (timeseriesResponse.data.success) {
        setTimeseriesData(timeseriesResponse.data.series || []);
      }

    } catch (err) {
      logger.error('Analytics fetch error:', err);
      setError(err.response?.data?.error || err.message || 'Failed to load analytics');
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  // Copy referral link
  const copyReferralLink = () => {
    if (!referralCode) return;

    const link = `${process.env.REACT_APP_PUBLIC_URL || window.location.origin}/r/${referralCode}`;
    navigator.clipboard.writeText(link);
    setCopiedLink(true);
    toast.success('Referral link copied to clipboard!');

    setTimeout(() => setCopiedLink(false), 2000);
  };

  // Export data
  const exportData = () => {
    if (!summaryData) return;

    const csvData = [
      ['Metric', 'Value'],
      ['Total Clicks', summaryData.totals.clicks],
      ['Total Trials', summaryData.totals.trials],
      ['Total Purchases', summaryData.totals.purchases],
      ['Trial Conversion', `${summaryData.totals.trial_conversion_percent}%`],
      ['Purchase Conversion', `${summaryData.totals.purchase_conversion_percent}%`],
      ['Window Revenue', `$${summaryData.revenue.window.total_revenue.toFixed(2)}`],
      ['Window Commission', `$${summaryData.revenue.window.total_commission.toFixed(2)}`],
      ['Lifetime Revenue', `$${summaryData.revenue.lifetime.total_revenue.toFixed(2)}`],
      ['Lifetime Commission', `$${summaryData.revenue.lifetime.total_commission.toFixed(2)}`],
    ];

    const csv = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `partner_analytics_${dateRange}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);

    toast.success('Analytics data exported');
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Format date
  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <div className="text-red-500 mb-4">
                <TrendingDown className="h-12 w-12 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Failed to Load Analytics</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={fetchAnalytics}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Partner Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Track your referral performance and earnings
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Date Range Selector */}
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
              <SelectItem value="1y">Last Year</SelectItem>
            </SelectContent>
          </Select>

          {/* Export Button */}
          <Button variant="outline" onClick={exportData}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>

          {/* Refresh Button */}
          <Button variant="outline" onClick={fetchAnalytics}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Referral Link Card */}
      {referralCode && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LinkIcon className="h-5 w-5" />
              Your Referral Link
            </CardTitle>
            <CardDescription>
              Share this link to earn {summaryData?.discount?.discount_percentage || 50}% commission on referrals
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="flex-1 p-3 bg-muted rounded-lg font-mono text-sm">
                {process.env.REACT_APP_PUBLIC_URL || window.location.origin}/r/{referralCode}
              </div>
              <Button onClick={copyReferralLink}>
                {copiedLink ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </>
                )}
              </Button>
            </div>
            <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Badge variant="outline">Code: {referralCode}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline">
                  {summaryData?.discount?.discount_percentage || 50}% First Payment
                </Badge>
              </div>
              {summaryData?.discount?.is_active && (
                <Badge variant="default" className="bg-green-500">Active</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Clicks */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clicks</CardTitle>
            <MousePointerClick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryData?.totals.clicks || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Lifetime: {summaryData?.lifetime.clicks || 0}
            </p>
          </CardContent>
        </Card>

        {/* Trials */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trials Started</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryData?.totals.trials || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {summaryData?.totals.trial_conversion_percent || 0}% conversion
            </p>
          </CardContent>
        </Card>

        {/* Purchases */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Purchases</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryData?.totals.purchases || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {summaryData?.totals.purchase_conversion_percent || 0}% conversion
            </p>
          </CardContent>
        </Card>

        {/* Commission */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Commission</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(summaryData?.revenue.window.total_commission || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Lifetime: {formatCurrency(summaryData?.revenue.lifetime.total_commission || 0)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Window Revenue */}
        <Card>
          <CardHeader>
            <CardTitle>Current Period Revenue</CardTitle>
            <CardDescription>Revenue for selected date range</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Revenue</span>
              <span className="text-lg font-semibold">
                {formatCurrency(summaryData?.revenue.window.total_revenue || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Your Commission</span>
              <span className="text-lg font-semibold text-green-600">
                {formatCurrency(summaryData?.revenue.window.total_commission || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Customer Discount</span>
              <span className="text-lg font-semibold">
                {formatCurrency(summaryData?.revenue.window.total_discount || 0)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Lifetime Revenue */}
        <Card>
          <CardHeader>
            <CardTitle>Lifetime Revenue</CardTitle>
            <CardDescription>All-time performance metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Revenue</span>
              <span className="text-lg font-semibold">
                {formatCurrency(summaryData?.revenue.lifetime.total_revenue || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Your Commission</span>
              <span className="text-lg font-semibold text-green-600">
                {formatCurrency(summaryData?.revenue.lifetime.total_commission || 0)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Customer Discount</span>
              <span className="text-lg font-semibold">
                {formatCurrency(summaryData?.revenue.lifetime.total_discount || 0)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="funnel">Conversion Funnel</TabsTrigger>
          <TabsTrigger value="referrals">Recent Referrals</TabsTrigger>
        </TabsList>

        {/* Performance Chart */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Over Time</CardTitle>
              <CardDescription>Track clicks, trials, and purchases</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeseriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="t"
                    tickFormatter={(value) => formatDate(value)}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => formatDate(value)}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="clicks"
                    stroke="#3b82f6"
                    name="Clicks"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="trials"
                    stroke="#10b981"
                    name="Trials"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="purchases"
                    stroke="#f59e0b"
                    name="Purchases"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Conversion Funnel */}
        <TabsContent value="funnel" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Conversion Funnel</CardTitle>
              <CardDescription>Track user journey from click to purchase</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Clicks */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Clicks</span>
                    <span className="text-2xl font-bold">{summaryData?.totals.clicks || 0}</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-12 relative overflow-hidden">
                    <div
                      className="bg-blue-500 h-full flex items-center justify-center text-white font-semibold"
                      style={{ width: '100%' }}
                    >
                      100%
                    </div>
                  </div>
                </div>

                {/* Trials */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Trials</span>
                    <span className="text-2xl font-bold">{summaryData?.totals.trials || 0}</span>
                  </div>
                  <div className="w-full bg-green-200 rounded-full h-12 relative overflow-hidden">
                    <div
                      className="bg-green-500 h-full flex items-center justify-center text-white font-semibold"
                      style={{
                        width: `${summaryData?.totals.trial_conversion_percent || 0}%`,
                        minWidth: '60px'
                      }}
                    >
                      {summaryData?.totals.trial_conversion_percent || 0}%
                    </div>
                  </div>
                </div>

                {/* Purchases */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Purchases</span>
                    <span className="text-2xl font-bold">{summaryData?.totals.purchases || 0}</span>
                  </div>
                  <div className="w-full bg-orange-200 rounded-full h-12 relative overflow-hidden">
                    <div
                      className="bg-orange-500 h-full flex items-center justify-center text-white font-semibold"
                      style={{
                        width: `${summaryData?.totals.purchase_conversion_percent || 0}%`,
                        minWidth: '60px'
                      }}
                    >
                      {summaryData?.totals.purchase_conversion_percent || 0}%
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recent Referrals */}
        <TabsContent value="referrals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Referrals</CardTitle>
              <CardDescription>Latest referred customers and their purchases</CardDescription>
            </CardHeader>
            <CardContent>
              {summaryData?.recent_referrals && summaryData.recent_referrals.length > 0 ? (
                <div className="space-y-4">
                  {summaryData.recent_referrals.map((referral, index) => (
                    <div
                      key={referral.id || index}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium">
                          {referral.user?.name || referral.user?.email || 'Anonymous'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(referral.payment_date).toLocaleDateString('en-US', {
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </div>
                      </div>
                      <div className="text-right space-y-1">
                        <div className="font-semibold">
                          {formatCurrency(referral.final_amount || 0)}
                        </div>
                        <div className="text-sm text-green-600">
                          +{formatCurrency(referral.commission_amount || 0)} commission
                        </div>
                        <Badge variant={referral.status === 'paid' ? 'default' : 'secondary'}>
                          {referral.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No referrals yet</p>
                  <p className="text-sm mt-2">Share your referral link to start earning</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
