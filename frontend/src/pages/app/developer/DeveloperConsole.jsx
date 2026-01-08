import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Textarea } from '../../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { Separator } from '../../../components/ui/separator';
import { Play, Copy, Download, AlertTriangle, Terminal, Code, Zap } from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { api } from '../../../api/client';
import { toast } from 'sonner';

const DeveloperConsole = () => {
  const { user } = useAuth();
  const [selectedEndpoint, setSelectedEndpoint] = useState('');
  const [method, setMethod] = useState('GET');
  const [requestUrl, setRequestUrl] = useState('');
  const [requestHeaders, setRequestHeaders] = useState('{\n  "Authorization": "Bearer YOUR_API_KEY",\n  "Content-Type": "application/json"\n}');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [responseTime, setResponseTime] = useState(null);

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  // Available endpoints for testing
  const endpoints = [
    { path: '/stocks/', method: 'GET', description: 'List all stocks' },
    { path: '/stocks/AAPL/', method: 'GET', description: 'Get specific stock' },
    { path: '/market-stats/', method: 'GET', description: 'Market statistics' },
    { path: '/trending/', method: 'GET', description: 'Trending stocks' },
    { path: '/portfolio/', method: 'GET', description: 'User portfolio' },
    { path: '/portfolio/add/', method: 'POST', description: 'Add to portfolio' },
    { path: '/alerts/create/', method: 'POST', description: 'Create alert' },
    { path: '/alerts/', method: 'GET', description: 'List alerts' },
    { path: '/screeners/', method: 'GET', description: 'List screeners' },
    { path: '/filter/', method: 'GET', description: 'Filter stocks' },
    { path: '/search/', method: 'GET', description: 'Search stocks' },
    { path: '/billing/current-plan/', method: 'GET', description: 'Current plan' },
    { path: '/user/profile/', method: 'GET', description: 'User profile' }
  ];

  const getDefaultApiOrigin = () => {
    const raw = (process.env.REACT_APP_BACKEND_URL || '').trim().replace(/\/$/, '');
    if (raw) return raw;
    if (process.env.NODE_ENV === 'production') return 'https://api.tradescanpro.com';
    return window.location.origin;
  };

  const toApiPath = (inputUrl) => {
    try {
      const u = new URL(inputUrl, window.location.origin);
      const pathname = u.pathname || '';
      const apiPrefix = '/api';
      const pathAfterApi = pathname.startsWith(apiPrefix) ? pathname.slice(apiPrefix.length) : pathname;
      return `${pathAfterApi || '/'}${u.search || ''}`;
    } catch {
      // If it's already a path like "/stocks/" or "/api/stocks/"
      const s = String(inputUrl || '').trim();
      if (s.startsWith('/api')) return s.replace(/^\/api/, '') || '/';
      return s || '/';
    }
  };

  const handleEndpointChange = (endpointPath) => {
    const endpoint = endpoints.find(e => e.path === endpointPath);
    if (endpoint) {
      setSelectedEndpoint(endpointPath);
      setMethod(endpoint.method);
      setRequestUrl(`${getDefaultApiOrigin()}/api${endpointPath}`);
      
      // Set example request body for POST endpoints
      if (endpoint.method === 'POST') {
        if (endpointPath === '/portfolio/add/') {
          setRequestBody('{\n  "symbol": "AAPL",\n  "shares": 10,\n  "avg_cost": 150.50\n}');
        } else if (endpointPath === '/alerts/create/') {
          setRequestBody('{\n  "ticker": "AAPL",\n  "target_price": 160,\n  "condition": "above",\n  "email": true\n}');
        } else {
          setRequestBody('{}');
        }
      } else {
        setRequestBody('');
      }
    }
  };

  const executeRequest = async () => {
    if (!requestUrl) {
      toast.error('Please enter a request URL');
      return;
    }

    setLoading(true);
    setResponse(null);
    setResponseTime(null);

    try {
      const startTime = Date.now();
      
      // Parse headers
      let headers = {};
      try {
        headers = JSON.parse(requestHeaders);
      } catch (e) {
        toast.error('Invalid JSON in headers');
        setLoading(false);
        return;
      }

      // Parse request body for POST requests
      let body = null;
      if (method === 'POST' && requestBody.trim()) {
        try {
          body = JSON.parse(requestBody);
        } catch (e) {
          toast.error('Invalid JSON in request body');
          setLoading(false);
          return;
        }
      }

      // Extract the API path from the full URL (supports full URLs or relative paths)
      const apiPath = toApiPath(requestUrl);
      
      let result;
      if (method === 'GET') {
        result = await api.get(apiPath);
      } else if (method === 'POST') {
        result = await api.post(apiPath, body);
      }

      const endTime = Date.now();
      setResponseTime(endTime - startTime);

      setResponse({
        status: result.status,
        statusText: result.statusText,
        headers: result.headers,
        data: result.data
      });

      toast.success('Request completed successfully');
    } catch (error) {
      const endTime = Date.now();
      setResponseTime(endTime - startTime);

      setResponse({
        status: error.response?.status || 0,
        statusText: error.response?.statusText || 'Network Error',
        headers: error.response?.headers || {},
        data: error.response?.data || { error: error.message }
      });

      toast.error('Request failed');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const exportResponse = () => {
    if (!response) return;
    
    const exportData = {
      request: {
        method,
        url: requestUrl,
        headers: JSON.parse(requestHeaders),
        body: requestBody ? JSON.parse(requestBody) : null
      },
      response: {
        status: response.status,
        statusText: response.statusText,
        data: response.data
      },
      responseTime,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `api-test-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status) => {
    if (status >= 200 && status < 300) return 'bg-green-100 text-green-800';
    if (status >= 400 && status < 500) return 'bg-red-100 text-red-800';
    if (status >= 500) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Developer Console</h1>
            <p className="text-gray-600">Interactive API testing and debugging tool</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                The Developer Console is available exclusively for Gold plan subscribers. Test API endpoints, debug responses, and export results.
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

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Terminal className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Developer Console</h1>
          </div>
          <p className="text-gray-600">Interactive API testing and debugging tool</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Request Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Request Configuration
                </CardTitle>
                <CardDescription>Configure your API request</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Endpoint Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quick Select Endpoint
                  </label>
                  <Select onValueChange={handleEndpointChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose an endpoint to test" />
                    </SelectTrigger>
                    <SelectContent>
                      {endpoints.map((endpoint) => (
                        <SelectItem key={endpoint.path} value={endpoint.path}>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {endpoint.method}
                            </Badge>
                            <span className="font-mono text-sm">{endpoint.path}</span>
                            <span className="text-gray-500">- {endpoint.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Method and URL */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Method
                    </label>
                    <Select value={method} onValueChange={setMethod}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="GET">GET</SelectItem>
                        <SelectItem value="POST">POST</SelectItem>
                        <SelectItem value="PUT">PUT</SelectItem>
                        <SelectItem value="DELETE">DELETE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Request URL
                    </label>
                    <Input
                      value={requestUrl}
                      onChange={(e) => setRequestUrl(e.target.value)}
                      placeholder="https://api.tradescanpro.com/api/..."
                    />
                  </div>
                </div>

                {/* Headers */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Headers (JSON)
                  </label>
                  <Textarea
                    value={requestHeaders}
                    onChange={(e) => setRequestHeaders(e.target.value)}
                    placeholder="Request headers in JSON format"
                    className="font-mono text-sm"
                    rows={4}
                  />
                </div>

                {/* Request Body (for POST requests) */}
                {method === 'POST' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Request Body (JSON)
                    </label>
                    <Textarea
                      value={requestBody}
                      onChange={(e) => setRequestBody(e.target.value)}
                      placeholder="Request body in JSON format"
                      className="font-mono text-sm"
                      rows={6}
                    />
                  </div>
                )}

                {/* Execute Button */}
                <Button 
                  onClick={executeRequest} 
                  disabled={loading || !requestUrl}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Execute Request
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Response Panel */}
          <div>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Response
                  </CardTitle>
                  {response && (
                    <div className="flex items-center gap-2">
                      {responseTime && (
                        <Badge variant="outline" className="text-xs">
                          {responseTime}ms
                        </Badge>
                      )}
                      <Badge className={`text-xs ${getStatusColor(response.status)}`}>
                        {response.status} {response.statusText}
                      </Badge>
                    </div>
                  )}
                </div>
                <CardDescription>
                  {response ? 'API response details' : 'Execute a request to see the response'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {response ? (
                  <Tabs defaultValue="body" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <TabsList>
                        <TabsTrigger value="body">Response Body</TabsTrigger>
                        <TabsTrigger value="headers">Headers</TabsTrigger>
                      </TabsList>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(JSON.stringify(response.data, null, 2))}
                        >
                          <Copy className="h-4 w-4 mr-1" />
                          Copy
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={exportResponse}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Export
                        </Button>
                      </div>
                    </div>

                    <TabsContent value="body">
                      <ScrollArea className="h-96 border rounded-lg">
                        <pre className="p-4 text-sm bg-gray-50">
                          <code>{JSON.stringify(response.data, null, 2)}</code>
                        </pre>
                      </ScrollArea>
                    </TabsContent>

                    <TabsContent value="headers">
                      <ScrollArea className="h-96 border rounded-lg">
                        <div className="p-4 space-y-2">
                          {Object.entries(response.headers).map(([key, value]) => (
                            <div key={key} className="flex items-start gap-4">
                              <code className="text-sm font-medium text-gray-900 min-w-32">
                                {key}:
                              </code>
                              <code className="text-sm text-gray-600 break-all">
                                {value}
                              </code>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </TabsContent>
                  </Tabs>
                ) : (
                  <div className="text-center py-12">
                    <Terminal className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Response Yet</h3>
                    <p className="text-gray-600">Configure and execute a request to see the response here.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Tips */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Developer Console Tips</CardTitle>
            <CardDescription>Make the most of your API testing experience</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Getting Started</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use the endpoint dropdown for quick setup</li>
                  <li>• Make sure your API key is set in headers</li>
                  <li>• Check response status codes for debugging</li>
                  <li>• Export responses for documentation</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Authentication</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Replace YOUR_API_KEY with your actual key</li>
                  <li>• Get API keys from <Link to="/app/developer/api-keys" className="text-blue-600 hover:underline">API Key Management</Link></li>
                  <li>• All requests require proper authentication</li>
                  <li>• Check headers if you get 401 errors</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DeveloperConsole;