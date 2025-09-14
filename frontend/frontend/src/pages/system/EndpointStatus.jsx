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
} from "lucide-react";
import { getEndpointStatus } from "../../api/client";

const EndpointStatus = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statusData, setStatusData] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState("");

  const fetchStatus = async (showRefreshing = false) => {
    if (showRefreshing) setIsRefreshing(true);
    setError("");

    try {
      const response = await getEndpointStatus();
      // Expect shape: { success, data }
      if (response?.success) {
        setStatusData(response.data);
        setLastUpdated(new Date());
      } else {
        setStatusData({ endpoints: [], total_tested: 0, successful: 0, failed: 0 });
        setError("Endpoint status not available");
        toast.error("Endpoint status not available");
      }
    } catch (e) {
      console.error("Failed to fetch status:", e);
      setStatusData({ endpoints: [], total_tested: 0, successful: 0, failed: 0 });
      setError("Failed to fetch endpoint status");
      toast.error("Failed to fetch endpoint status");
    } finally {
      setIsLoading(false);
      if (showRefreshing) setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => fetchStatus(), 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getResponseTimeColor = (responseTime) => {
    if (!responseTime) return "text-gray-500";
    if (responseTime < 100) return "text-green-600";
    if (responseTime < 300) return "text-yellow-600";
    return "text-red-600";
  };

  const overallStatus =
    statusData?.successful === statusData?.total_tested ? "operational" : "degraded";

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
            <p className="text-gray-600 mt-2">Real-time status of API endpoints</p>
          </div>

          <Button onClick={() => fetchStatus(true)} disabled={isRefreshing} variant="outline">
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </Button>
        </div>

        {error && (
          <Card className="border-l-4 border-l-yellow-500 bg-yellow-50/50">
            <CardContent className="p-4 text-yellow-800">{error}</CardContent>
          </Card>
        )}

        {/* Overall Status */}
        <Card className={`border-l-4 ${overallStatus === "operational" ? "border-l-green-500 bg-green-50/50" : "border-l-yellow-500 bg-yellow-50/50"}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {overallStatus === "operational" ? (
                  <CheckCircle className="h-8 w-8 text-green-500" />
                ) : (
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                )}
                <div>
                  <h2 className="text-xl font-semibold">
                    {overallStatus === "operational" ? "All Systems Operational" : "Some Services Degraded"}
                  </h2>
                  <p className="text-gray-600">
                    {statusData?.successful} of {statusData?.total_tested} services are running
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
                    {statusData?.endpoints && statusData.endpoints.filter((e) => e.response_time).length
                      ? `${Math.round(
                          statusData.endpoints
                            .filter((e) => e.response_time)
                            .reduce((acc, e) => acc + e.response_time, 0) /
                            statusData.endpoints.filter((e) => e.response_time).length
                        )}ms`
                      : "-"}
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
              <Server className="h-5 w-5 mr-2" /> API Endpoints
            </CardTitle>
            <CardDescription>Detailed status of all API endpoints</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-0 divide-y">
              {(statusData?.endpoints || []).map((endpoint, index) => (
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
                      <div className="font-medium">Status {endpoint.status_code ?? "-"}</div>
                      {endpoint.response_time && (
                        <div className={`text-sm ${getResponseTimeColor(endpoint.response_time)}`}>
                          <Clock className="h-3 w-3 inline mr-1" />
                          {endpoint.response_time}ms
                        </div>
                      )}
                    </div>
                    <Badge className={endpoint.status === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                      {endpoint.status === "success" ? "Online" : "Offline"}
                    </Badge>
                  </div>
                </div>
              ))}

              {!statusData?.endpoints?.length && (
                <div className="py-8 text-center text-gray-500">No endpoints reported</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          This page auto-refreshes every 30s.
        </div>
      </div>
    </div>
  );
};

export default EndpointStatus;