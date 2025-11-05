import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { Separator } from '../../../components/ui/separator';
import { Search, Book, Code, AlertTriangle, Copy, ExternalLink, Play } from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { getApiDocumentation } from '../../../api/client';
import { toast } from 'sonner';

const ApiDocumentation = () => {
  const { user } = useAuth();
  const [documentation, setDocumentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);

  // Check if user has Gold plan
  const hasGoldPlan = user?.plan === 'gold';

  useEffect(() => {
    if (hasGoldPlan) {
      loadDocumentation();
    } else {
      setLoading(false);
    }
  }, [hasGoldPlan]);

  const loadDocumentation = async () => {
    try {
      const response = await getApiDocumentation();
      if (response.success) {
        setDocumentation(response.data);
      } else {
        // Use mock documentation if API doesn't return data
        setDocumentation(mockDocumentation);
      }
    } catch (error) {
      console.error('Failed to load API documentation:', error);
      setDocumentation(mockDocumentation);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const filteredEndpoints = documentation?.endpoints?.filter(endpoint =>
    endpoint.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    endpoint.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    endpoint.method.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Mock documentation data
  const mockDocumentation = {
    title: "Trade Scan Pro API Documentation",
    version: "v1.0",
      base_url: "https://api.tradescanpro.com/api",
    endpoints: [
      {
        id: 1,
        path: "/stocks/",
        method: "GET",
        description: "List all stocks with pagination and filtering",
        parameters: [
          { name: "page", type: "integer", required: false, description: "Page number (default: 1)" },
          { name: "limit", type: "integer", required: false, description: "Results per page (default: 50)" },
          { name: "search", type: "string", required: false, description: "Search by ticker or company name" },
          { name: "min_price", type: "number", required: false, description: "Minimum stock price" },
          { name: "max_price", type: "number", required: false, description: "Maximum stock price" },
          { name: "exchange", type: "string", required: false, description: "Exchange (NYSE, NASDAQ)" }
        ],
        response: {
          success: true,
          data: [
            {
              ticker: "AAPL",
              company_name: "Apple Inc.",
              current_price: 150.25,
              change_percent: 2.34,
              volume: 45678900,
              market_cap: 2450000000000
            }
          ],
          count: 1,
          total_pages: 100
        },
        example: `curl -H "Authorization: Bearer YOUR_API_KEY" \\
       "https://api.tradescanpro.com/api/stocks/?limit=10&min_price=50"`
      },
      {
        id: 2,
        path: "/stocks/{ticker}/",
        method: "GET",
        description: "Get detailed information for a specific stock",
        parameters: [
          { name: "ticker", type: "string", required: true, description: "Stock ticker symbol (e.g., AAPL)" }
        ],
        response: {
          success: true,
          data: {
            ticker: "AAPL",
            company_name: "Apple Inc.",
            current_price: 150.25,
            change_percent: 2.34,
            volume: 45678900,
            market_cap: 2450000000000,
            recent_prices: [
              { price: 148.50, timestamp: "2024-01-15T16:00:00Z" },
              { price: 150.25, timestamp: "2024-01-16T16:00:00Z" }
            ]
          }
        },
        example: `curl -H "Authorization: Bearer YOUR_API_KEY" \\
       "https://api.tradescanpro.com/api/stocks/AAPL/"`
      },
      {
        id: 3,
        path: "/portfolio/",
        method: "GET",
        description: "Get user's portfolio holdings",
        parameters: [],
        response: {
          success: true,
          data: [
            {
              id: "holding_123",
              symbol: "AAPL",
              shares: 10,
              avg_cost: 145.50,
              current_price: 150.25,
              total_value: 1502.50,
              gain_loss: 47.50,
              gain_loss_percent: 3.26
            }
          ],
          summary: {
            total_value: 15025.00,
            total_gain_loss: 475.00,
            total_gain_loss_percent: 3.26
          }
        },
        example: `curl -H "Authorization: Bearer YOUR_API_KEY" \\
       "https://api.tradescanpro.com/api/portfolio/"`
      },
      {
        id: 4,
        path: "/alerts/create/",
        method: "POST",
        description: "Create a new price alert",
        parameters: [
          { name: "ticker", type: "string", required: true, description: "Stock ticker symbol" },
          { name: "target_price", type: "number", required: true, description: "Alert trigger price" },
          { name: "condition", type: "string", required: true, description: "Condition: 'above' or 'below'" },
          { name: "email", type: "boolean", required: false, description: "Send email notification" }
        ],
        response: {
          success: true,
          alert_id: "alert_456",
          message: "Alert created successfully"
        },
        example: `curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{"ticker":"AAPL","target_price":160,"condition":"above","email":true}' \\
       "https://api.tradescanpro.com/api/alerts/create/"`
      },
      {
        id: 5,
        path: "/market-stats/",
        method: "GET",
        description: "Get overall market statistics and overview",
        parameters: [],
        response: {
          success: true,
          market_overview: {
            total_stocks: 8000,
            gainers: 3200,
            losers: 2800,
            unchanged: 2000
          },
          top_gainers: [],
          top_losers: [],
          most_active: []
        },
        example: `curl -H "Authorization: Bearer YOUR_API_KEY" \\
       "https://api.tradescanpro.com/api/market-stats/"`
      }
    ]
  };

  if (!hasGoldPlan) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">API Documentation</h1>
            <p className="text-gray-600">Complete reference for Trade Scan Pro API</p>
          </div>

          <Alert className="border-amber-200 bg-amber-50">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <AlertDescription className="text-amber-800">
              <div className="font-semibold mb-2">Gold Plan Required</div>
              <p className="mb-4">
                Complete API documentation and developer resources are available exclusively for Gold plan subscribers.
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
            <p className="text-gray-600">Loading API documentation...</p>
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
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">API Documentation</h1>
              <p className="text-gray-600">Complete reference for Trade Scan Pro API</p>
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              Version {documentation?.version || 'v1.0'}
            </Badge>
          </div>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search endpoints..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Endpoints List */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Book className="h-5 w-5" />
                  Endpoints
                </CardTitle>
                <CardDescription>
                  {filteredEndpoints.length} endpoint{filteredEndpoints.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  <div className="space-y-1 p-4">
                    {filteredEndpoints.map((endpoint) => (
                      <div
                        key={endpoint.id}
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          selectedEndpoint?.id === endpoint.id
                            ? 'bg-blue-50 border border-blue-200'
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => setSelectedEndpoint(endpoint)}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <Badge 
                            variant={endpoint.method === 'GET' ? 'secondary' : 'default'}
                            className={`text-xs ${
                              endpoint.method === 'GET' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {endpoint.method}
                          </Badge>
                        </div>
                        <div className="font-mono text-sm text-gray-900 mb-1">
                          {endpoint.path}
                        </div>
                        <div className="text-xs text-gray-600 line-clamp-2">
                          {endpoint.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Endpoint Details */}
          <div className="lg:col-span-2">
            {selectedEndpoint ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <Badge 
                          variant={selectedEndpoint.method === 'GET' ? 'secondary' : 'default'}
                          className={`${
                            selectedEndpoint.method === 'GET' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {selectedEndpoint.method}
                        </Badge>
                        <code className="text-lg font-mono bg-gray-100 px-2 py-1 rounded">
                          {selectedEndpoint.path}
                        </code>
                      </div>
                      <p className="text-gray-600">{selectedEndpoint.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="parameters" className="space-y-6">
                    <TabsList>
                      <TabsTrigger value="parameters">Parameters</TabsTrigger>
                      <TabsTrigger value="response">Response</TabsTrigger>
                      <TabsTrigger value="example">Example</TabsTrigger>
                    </TabsList>

                    <TabsContent value="parameters" className="space-y-4">
                      {selectedEndpoint.parameters.length > 0 ? (
                        <div className="space-y-4">
                          {selectedEndpoint.parameters.map((param, index) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-4">
                              <div className="flex items-center gap-3 mb-2">
                                <code className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                                  {param.name}
                                </code>
                                <Badge variant="outline" className="text-xs">
                                  {param.type}
                                </Badge>
                                {param.required && (
                                  <Badge variant="default" className="text-xs bg-red-100 text-red-800">
                                    Required
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-600">{param.description}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-600">No parameters required for this endpoint.</p>
                      )}
                    </TabsContent>

                    <TabsContent value="response" className="space-y-4">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-gray-900">Response Format</h4>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(JSON.stringify(selectedEndpoint.response, null, 2))}
                          >
                            <Copy className="h-4 w-4 mr-2" />
                            Copy
                          </Button>
                        </div>
                        <pre className="text-sm bg-white p-3 rounded border overflow-x-auto">
                          <code>{JSON.stringify(selectedEndpoint.response, null, 2)}</code>
                        </pre>
                      </div>
                    </TabsContent>

                    <TabsContent value="example" className="space-y-4">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-gray-900">cURL Example</h4>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(selectedEndpoint.example)}
                          >
                            <Copy className="h-4 w-4 mr-2" />
                            Copy
                          </Button>
                        </div>
                        <pre className="text-sm bg-white p-3 rounded border overflow-x-auto">
                          <code>{selectedEndpoint.example}</code>
                        </pre>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Select an Endpoint</h3>
                  <p className="text-gray-600">Choose an endpoint from the list to view detailed documentation.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Getting Started Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Quick guide to using the Trade Scan Pro API</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Authentication</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>All API requests require authentication using your API key:</p>
                  <div className="bg-gray-50 p-3 rounded font-mono text-xs">
                    Authorization: Bearer YOUR_API_KEY
                  </div>
                  <p>Get your API key from the <Link to="/app/developer/api-keys" className="text-blue-600 hover:underline">API Key Management</Link> page.</p>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Base URL</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>All API endpoints are relative to:</p>
                    <div className="bg-gray-50 p-3 rounded font-mono text-xs break-all">
                      {documentation?.base_url || 'https://api.tradescanpro.com/api'}
                  </div>
                  <p>All responses are in JSON format.</p>
                </div>
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Rate Limits</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <p>Gold plan subscribers enjoy unlimited API access with no rate limits.</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Unlimited requests per month</li>
                  <li>Real-time data access</li>
                  <li>No throttling or delays</li>
                  <li>Priority support</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ApiDocumentation;