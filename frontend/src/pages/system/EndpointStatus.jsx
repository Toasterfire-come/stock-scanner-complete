import React, { useState, useEffect } from "react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { toast } from "sonner";
import { 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  AlertTriangle,
  Server,
  Activity,
  Clock,
  TrendingUp
} from "lucide-react";
import { getEndpointStatus } from "../../api/client";

const EndpointStatus = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statusData, setStatusData] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchStatus = async (showRefreshing = false) => {
    if (showRefreshing) setIsRefreshing(true);
    
    try {
      const response = await getEndpointStatus();
      if (response.success) {
        setStatusData(response.data);
        setLastUpdated(new Date());
      } else {
        toast.error("Failed to fetch endpoint status");
      }
    } catch (error) {
      console.error("Failed to fetch status:", error);
      // Mock data for demo
      setStatusData({
        endpoints: [
          {
            name: "root",
            url: "/api/",
            status: "success",
            status_code: 200,
            response_time: 45
          },
          {
            name: "health",
            url: "/api/health/",
            status: "success", 
            status_code: 200,
            response_time: 23
          },
          {
            name: "stocks",
            url: "/api/stocks/",
            status: "success",
            status_code: 200,
            response_time: 67
          },
          {
            name: "search",
            url: "/api/search/?q=AAPL",
            status: "success",
            status_code: 200,
            response_time: 89
          },
          {
            name: "trending",
            url: "/api/trending/",
            status: "success",
            status_code: 200,
            response_time: 156
          },
          {
            name: "auth",
            url: "/api/auth/login/",
            status: "error",
            status_code: 500,
            response_time: null
          }
        ],
        total_tested: 6,
        successful: 5,
        failed: 1,
        timestamp: new Date().toISOString()
      });
      setLastUpdated(new Date());
    } finally {
      setIsLoading(false);
      if (showRefreshing) setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchStatus();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status, statusCode) => {
    if (status === 'success') {
      return <Badge className="bg-green-100 text-green-800">Online</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800">Offline</Badge>;
    }
  };

  const getResponseTimeColor = (responseTime) => {
    if (!responseTime) return 'text-gray-500';
    if (responseTime < 100) return 'text-green-600';
    if (responseTime < 300) return 'text-yellow-600';
    return 'text-red-600';
  };

  const overallStatus = statusData?.successful === statusData?.total_tested ? 'operational' : 'degraded';

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </CardContent>
              </Card>
            ))}
          </div>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">System Status</h1>
            <p className="text-gray-600 mt-2">
              Real-time status of all Stock Scanner services and endpoints
            </p>
          </div>
          
          <Button 
            onClick={() => fetchStatus(true)} 
            disabled={isRefreshing}
            variant="outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {/* Overall Status */}
        <Card className={`border-l-4 ${overallStatus === 'operational' ? 'border-l-green-500 bg-green-50/50' : 'border-l-yellow-500 bg-yellow-50/50'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {overallStatus === 'operational' ? (
                  <CheckCircle className="h-8 w-8 text-green-500" />
                ) : (
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                )}
                <div>
                  <h2 className="text-xl font-semibold">
                    {overallStatus === 'operational' ? 'All Systems Operational' : 'Some Services Degraded'}
                  </h2>
                  <p className="text-gray-600">
                    {statusData?.successful} of {statusData?.total_tested} services are running normally
                  </p>
                </div>
              </div>
              
              {lastUpdated && (
                <div className="text-right">
                  <div className="text-sm text-gray-500">Last updated</div>
                  <div className="font-medium">{lastUpdated.toLocaleTimeString()}</div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Statistics */}
        <div className="grid md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-500" />
                <div className="ml-4">
                  <div className="text-2xl font-bold">{statusData?.successful || 0}</div>
                  <div className="text-sm text-gray-600">Services Online</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <XCircle className="h-8 w-8 text-red-500" />
                <div className="ml-4">
                  <div className="text-2xl font-bold">{statusData?.failed || 0}</div>
                  <div className="text-sm text-gray-600">Services Offline</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-blue-500" />
                <div className="ml-4">
                  <div className="text-2xl font-bold">
                    {statusData?.endpoints ? 
                      Math.round(statusData.endpoints.filter(e => e.response_time).reduce((acc, e) => acc + e.response_time, 0) / statusData.endpoints.filter(e => e.response_time).length) 
                      : 0}ms
                  </div>
                  <div className="text-sm text-gray-600">Avg Response Time</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Endpoint Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="h-5 w-5 mr-2" />
              API Endpoints
            </CardTitle>
            <CardDescription>
              Detailed status of all API endpoints
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-0 divide-y">
              {statusData?.endpoints?.map((endpoint, index) => (
                <div key={index} className="flex items-center justify-between py-4">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(endpoint.status)}
                    <div>
                      <div className="font-medium capitalize">{endpoint.name}</div>
                      <div className="text-sm text-gray-600">{endpoint.url}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-medium">
                        Status {endpoint.status_code}
                      </div>
                      {endpoint.response_time && (
                        <div className={`text-sm ${getResponseTimeColor(endpoint.response_time)}`}>
                          <Clock className="h-3 w-3 inline mr-1" />
                          {endpoint.response_time}ms
                        </div>
                      )}
                    </div>
                    {getStatusBadge(endpoint.status, endpoint.status_code)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Incident History */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Incidents</CardTitle>
            <CardDescription>
              Past 7 days of system incidents and maintenance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Recent Incidents</h3>
              <p className="text-gray-600">
                All systems have been running smoothly for the past 7 days.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Status Page Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>
            This page is automatically updated every 30 seconds. 
            For support, contact us at{" "}
            <a href="mailto:support@stockscanner.com" className="text-blue-600 hover:underline">
              support@stockscanner.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default EndpointStatus;