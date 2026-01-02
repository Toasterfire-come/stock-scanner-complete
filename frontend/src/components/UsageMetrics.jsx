import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { RefreshCw, Pause, Play, AlertTriangle, TrendingUp } from "lucide-react";

const UsageMetrics = ({ user }) => {
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    fetchUsageData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchUsageData, 300000);
    return () => clearInterval(interval);
  }, [user]);

  const fetchUsageData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/billing/usage/current/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch usage data');
      }

      const data = await response.json();
      setUsageData(data);
      setIsPaused(data.is_paused || false);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseToggle = async () => {
    try {
      const endpoint = isPaused ? '/api/billing/usage/unpause/' : '/api/billing/usage/pause/';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to toggle pause state');
      }

      setIsPaused(!isPaused);
      fetchUsageData(); // Refresh data
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const calculatePercentage = (current, quota) => {
    if (!quota || quota === 0) return 0;
    return Math.min(Math.round((current / quota) * 100), 100);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 90) return 'bg-orange-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  if (loading && !usageData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Usage & Limits</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
            <p className="ml-2 text-gray-600">Loading usage data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Usage Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8">
            <AlertTriangle className="h-8 w-8 text-red-500 mb-2" />
            <p className="text-red-600 mb-4">Error: {error}</p>
            <Button onClick={fetchUsageData} variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!usageData) {
    return null;
  }

  const { plan, usage, costs, alerts } = usageData;
  const isPayPerUse = plan === 'pay-per-use';

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Usage & Limits</CardTitle>
            <CardDescription className="mt-1">
              Track your monthly resource consumption
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="capitalize">
              {plan?.replace('-', ' ') || 'FREE'} PLAN
            </Badge>
            {isPayPerUse && isPaused && (
              <Badge variant="destructive">PAUSED</Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Cost Summary for Pay-Per-Use */}
        {isPayPerUse && costs && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-2">
            <h4 className="font-semibold text-purple-900 mb-3">Current Month Costs</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Base Price:</span>
                <span className="font-semibold">${costs.base?.toFixed(2) || '24.99'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Overages:</span>
                <span className="font-semibold text-orange-600">${costs.overages?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between col-span-2 pt-2 border-t border-purple-200">
                <span className="font-semibold text-gray-900">Current Total:</span>
                <span className="font-bold text-lg">${costs.total?.toFixed(2) || '24.99'}</span>
              </div>
              <div className="flex justify-between col-span-2 text-xs text-gray-500">
                <span>Monthly Cap:</span>
                <span className="font-semibold">${costs.hard_cap?.toFixed(2) || '124.99'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Usage Progress Bars */}
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900">Resource Usage</h4>
          {usage && Object.keys(usage).map((resourceKey) => {
            const resource = usage[resourceKey];
            const percentage = calculatePercentage(resource.current, resource.quota);
            const isOverage = resource.overage > 0;

            return (
              <div key={resourceKey} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-700 capitalize">
                    {resourceKey.replace(/_/g, ' ')}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600">
                      {resource.current?.toLocaleString() || 0} / {resource.quota?.toLocaleString() || '∞'}
                    </span>
                    {isOverage && (
                      <Badge variant="warning" className="bg-orange-100 text-orange-700">
                        +{resource.overage?.toLocaleString()}
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="relative">
                  <Progress value={percentage} className="h-2" />
                  <span className="text-xs text-gray-500 mt-1 block">
                    {percentage}% used
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Alerts */}
        {alerts && alerts.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Usage Alerts
            </h4>
            <div className="space-y-2">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-2 p-3 rounded-lg text-sm ${
                    alert.type === 'danger' ? 'bg-red-50 text-red-800' :
                    alert.type === 'warning' ? 'bg-orange-50 text-orange-800' :
                    'bg-yellow-50 text-yellow-800'
                  }`}
                >
                  <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{alert.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pause/Resume Controls for Pay-Per-Use */}
        {isPayPerUse && (
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            <h4 className="font-semibold text-gray-900">Usage Controls</h4>
            <p className="text-sm text-gray-600">
              {isPaused
                ? 'Usage is paused. Resume to continue making API calls and using features.'
                : 'Pause usage to prevent additional overage charges this month.'}
            </p>
            <Button
              onClick={handlePauseToggle}
              variant={isPaused ? "default" : "outline"}
              className="w-full"
            >
              {isPaused ? (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Resume Usage
                </>
              ) : (
                <>
                  <Pause className="h-4 w-4 mr-2" />
                  Pause at Current Limit
                </>
              )}
            </Button>
          </div>
        )}

        {/* Forecast for Pay-Per-Use */}
        {isPayPerUse && costs && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
            <h4 className="font-semibold text-blue-900 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              End-of-Month Forecast
            </h4>
            <p className="text-sm text-blue-700">
              Based on your current usage trend, your estimated bill for this month is:
            </p>
            <div className="text-3xl font-bold text-blue-900">
              ${costs.forecasted_total?.toFixed(2) || costs.total?.toFixed(2) || '24.99'}
            </div>
            <p className="text-xs text-blue-600">
              Estimate based on {costs.days_elapsed || 0} days of usage. Your actual bill may vary.
            </p>
          </div>
        )}

        {/* Refresh Button */}
        <div className="flex items-center justify-between pt-4 border-t">
          <span className="text-xs text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
          <Button onClick={fetchUsageData} variant="ghost" size="sm" disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default UsageMetrics;
