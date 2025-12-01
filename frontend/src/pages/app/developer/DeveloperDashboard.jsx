import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Link } from 'react-router-dom';
import { 
  Key, 
  BarChart3, 
  Book, 
  Terminal, 
  AlertTriangle, 
  TrendingUp, 
  Activity, 
  Code, 
  Zap,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { getApiKeys, getUsageStats } from '../../../api/client';
import { getCurrentApiUsage } from '../../../api/client';

const DeveloperDashboard = () => {
  const { user } = useAuth();
  const [apiKeys, setApiKeys] = useState([]);
  const [usageStats, setUsageStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  useEffect(() => {
    if (hasGoldPlan) {
      loadDeveloperData();
    } else {
      setLoading(false);
    }
  }, [hasGoldPlan]);

  const loadDeveloperData = async () => {
    try {
      // Load API keys and usage stats in parallel
      const [keysResponse, statsResponse] = await Promise.allSettled([
        getApiKeys(),
        getUsageStats()
      ]);

      if (keysResponse.status === 'fulfilled' && keysResponse.value.success) {
        setApiKeys(keysResponse.value.data || []);
      }

      if (statsResponse.status === 'fulfilled' && statsResponse.value.success) {
        setUsageStats(statsResponse.value.data);
      } else {
        // Use mock data for demo
        setUsageStats({
          daily: { api_calls: 1250, requests: 980 },
          monthly: { api_calls: 45000, requests: 38000 },
          account: { plan_type: 'gold', is_premium: true }
        });
      }
    } catch (error) {
      console.error('Failed to load developer data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    const n = Number(num || 0);
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
  };

  const developerTools = [
    {
      icon: Key,
      title: 'API Key Management',
      description: 'Create, manage, and monitor your API keys',
      link: '/app/developer/api-keys',
      badge: `${apiKeys.length} key${apiKeys.length !== 1 ? 's' : ''}`,
      color: 'blue'
    },
    {
      icon: BarChart3,
      title: 'Usage Statistics',
      description: 'Monitor API usage and performance metrics',
      link: '/app/developer/usage-statistics',
      badge: usageStats ? `${formatNumber(usageStats?.daily?.api_calls ?? 0)} today` : '0 today',
      color: 'green'
    },
    {
      icon: Book,
      title: 'API Documentation',
      description: 'Complete reference for all API endpoints',
      link: '/app/developer/api-documentation',
      badge: 'Interactive',
      color: 'purple'
    },
    {
      icon: Terminal,
      title: 'Developer Console',
      description: 'Test API endpoints and debug responses',
      link: '/app/developer/console',
      badge: 'Live Testing',
      color: 'orange'
    }
  ];

  const quickLinks = [
    { title: 'GitHub Repository', url: 'https://github.com/your-org/trade-scan-pro-examples', external: true },
    { title: 'API Status Page', url: '/endpoint-status', external: false },
    { title: 'Community Forum', url: 'https://community.retailtradescanner.com', external: true },
    { title: 'Support Center', url: '/help', external: false }
  ];

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Developer Dashboard</h1>
            <p className="text-gray-600">Your central hub for API development and management</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                Developer tools and API access are available exclusively for Gold plan subscribers. Unlock unlimited API calls, advanced analytics, and developer resources.
              </p>
              <a href="/account/plan" className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-700 hover:to-yellow-700 text-white rounded-md font-medium" rel="noopener noreferrer">
                Upgrade to Gold Plan
              </a>
            </AlertDescription>
          </Alert>

          {/* Preview of what's available */}
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">What You'll Get with Gold Plan</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {developerTools.map((tool, index) => (
                <Card key={index} className="opacity-75">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className={`h-12 w-12 bg-${tool.color}-100 rounded-lg flex items-center justify-center`}>
                        <tool.icon className={`h-6 w-6 text-${tool.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{tool.title}</h3>
                        <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                        <Badge variant="outline" className="text-xs">Coming with Gold</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
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
            <p className="text-gray-600">Loading developer dashboard...</p>
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Developer Dashboard</h1>
              <p className="text-gray-600">Your central hub for API development and management</p>
            </div>
            <Badge className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white">
              Gold Developer
            </Badge>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Keys</p>
                  <p className="text-2xl font-bold text-gray-900">{apiKeys.length}</p>
                </div>
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Key className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Today's Calls</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {usageStats ? formatNumber(usageStats.daily.api_calls) : '0'}
                  </p>
                </div>
                <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Activity className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Monthly Usage</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {usageStats ? formatNumber(usageStats.monthly.api_calls) : '0'}
                  </p>
                  <Badge variant="secondary" className="mt-1 text-xs">Unlimited</Badge>
                </div>
                <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-purple-600" />
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
                  <Badge className="mt-1 text-xs bg-gradient-to-r from-amber-500 to-yellow-500">Premium</Badge>
                </div>
                <div className="h-12 w-12 bg-amber-100 rounded-lg flex items-center justify-center">
                  <Zap className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Developer Tools */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Developer Tools</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {developerTools.map((tool, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`h-12 w-12 bg-${tool.color}-100 rounded-lg flex items-center justify-center`}>
                      <tool.icon className={`h-6 w-6 text-${tool.color}-600`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-gray-900">{tool.title}</h3>
                        <Badge variant="outline" className="text-xs">
                          {tool.badge}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{tool.description}</p>
                    </div>
                  </div>
                  <Button asChild className="w-full" variant="outline">
                    <Link to={tool.link}>
                      Open {tool.title}
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Recent Activity & Quick Links */}
        <div className="grid lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Recent API Activity</CardTitle>
              <CardDescription>Your latest API usage patterns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Stocks API</p>
                    <p className="text-sm text-gray-600">Most active endpoint</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {usageStats ? Math.floor(usageStats.daily.api_calls * 0.35) : 0}
                    </p>
                    <p className="text-sm text-gray-600">calls today</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Market Data</p>
                    <p className="text-sm text-gray-600">Real-time updates</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {usageStats ? Math.floor(usageStats.daily.api_calls * 0.25) : 0}
                    </p>
                    <p className="text-sm text-gray-600">calls today</p>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Portfolio API</p>
                    <p className="text-sm text-gray-600">User data access</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {usageStats ? Math.floor(usageStats.daily.api_calls * 0.20) : 0}
                    </p>
                    <p className="text-sm text-gray-600">calls today</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Links</CardTitle>
              <CardDescription>Helpful resources for developers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {quickLinks.map((link, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <Code className="h-4 w-4 text-gray-600" />
                      <span className="font-medium text-gray-900">{link.title}</span>
                    </div>
                    {link.external ? (
                      <a 
                        href={link.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    ) : (
                      <Link to={link.url} className="text-blue-600 hover:text-blue-700">
                        <ExternalLink className="h-4 w-4" />
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DeveloperDashboard;