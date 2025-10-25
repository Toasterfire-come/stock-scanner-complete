import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Activity, 
  Clock, 
  TrendingUp, 
  Eye, 
  Bell, 
  BarChart3,
  RefreshCw,
  Calendar
} from 'lucide-react';
import { getUserActivityFeed, getUserInsights } from '../api/client';
import { Link } from 'react-router-dom';

const RealUserActivityFeed = ({ maxItems = 10, showHeader = true }) => {
  const [activities, setActivities] = useState([]);
  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchActivityData();
    // Refresh activity feed every 5 minutes
    const interval = setInterval(fetchActivityData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivityData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [activityRes, insightsRes] = await Promise.all([
        getUserActivityFeed().catch(() => ({ success: false, data: [] })),
        getUserInsights().catch(() => null)
      ]);

      if (activityRes.success && Array.isArray(activityRes.data)) {
        setActivities(activityRes.data.slice(0, maxItems));
      } else {
        setActivities([]);
      }
      
      if (insightsRes?.success) {
        setInsights(insightsRes.insights);
      }
      
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to load activity feed');
      console.error('Activity feed error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getActivityIcon = (actionType) => {
    switch (actionType?.toLowerCase()) {
      case 'portfolio_add':
      case 'portfolio_update':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'watchlist_add':
      case 'watchlist_create':
        return <Eye className="h-4 w-4 text-blue-600" />;
      case 'alert_create':
      case 'alert_triggered':
        return <Bell className="h-4 w-4 text-yellow-600" />;
      case 'screener_run':
      case 'screener_create':
        return <BarChart3 className="h-4 w-4 text-purple-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActivityColor = (actionType) => {
    switch (actionType?.toLowerCase()) {
      case 'portfolio_add':
      case 'portfolio_update':
        return 'bg-green-100 text-green-800';
      case 'watchlist_add':
      case 'watchlist_create':
        return 'bg-blue-100 text-blue-800';
      case 'alert_create':
      case 'alert_triggered':
        return 'bg-yellow-100 text-yellow-800';
      case 'screener_run':
      case 'screener_create':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown time';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const formatActionType = (actionType) => {
    if (!actionType) return 'Activity';
    return actionType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (isLoading && activities.length === 0) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest trading activities</CardDescription>
          </CardHeader>
        )}
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading activity feed...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      {showHeader && (
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Recent Activity
              {lastUpdated && (
                <Badge variant="secondary" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatTimestamp(lastUpdated)}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>Your latest trading activities</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={fetchActivityData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/app/activity">
                <Calendar className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </CardHeader>
      )}
      
      <CardContent>
        {error && (
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Activity Insights */}
        {insights && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-blue-900">Activity Summary</h4>
              <Badge variant="secondary">{insights.activity_count} total activities</Badge>
            </div>
            {insights.top_endpoint_types && insights.top_endpoint_types.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {insights.top_endpoint_types.slice(0, 3).map((endpoint, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {formatActionType(endpoint.endpoint_type)}: {endpoint.count}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}

        {activities.length > 0 ? (
          <div className="space-y-3">
            {activities.map((activity, index) => (
              <div key={activity.id || index} 
                   className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex-shrink-0 mt-0.5">
                  {getActivityIcon(activity.action_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getActivityColor(activity.action_type)}`}
                    >
                      {formatActionType(activity.action_type)}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-900 mb-1">
                    {activity.details || 'Activity performed'}
                  </p>
                  {activity.symbol && (
                    <p className="text-xs text-gray-600">
                      Symbol: <span className="font-mono font-medium">{activity.symbol}</span>
                    </p>
                  )}
                  {activity.value && (
                    <p className="text-xs text-gray-600">
                      Value: <span className="font-medium">${activity.value}</span>
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <Activity className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p>No recent activity</p>
              <p className="text-sm">Your trading activities will appear here</p>
              <div className="mt-4 space-x-2">
                <Button variant="outline" size="sm" asChild>
                  <Link to="/app/stocks">Browse Stocks</Link>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/app/screeners">Create Screener</Link>
                </Button>
              </div>
            </div>
          </div>
        )}

        {activities.length >= maxItems && (
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm" asChild>
              <Link to="/app/activity">
                View All Activity
                <Activity className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RealUserActivityFeed;