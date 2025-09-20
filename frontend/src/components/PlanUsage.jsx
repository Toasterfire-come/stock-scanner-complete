import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { AlertTriangle, TrendingUp, Zap, Shield, Crown } from 'lucide-react';

const PlanUsage = ({ className = "" }) => {
  const [planData, setPlanData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPlanData();
  }, []);

  const fetchPlanData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/user/plan/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPlanData(data);
      } else {
        setError('Failed to load plan information');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getPlanIcon = (planType) => {
    switch (planType) {
      case 'free': return <Zap className="h-4 w-4" />;
      case 'bronze': return <TrendingUp className="h-4 w-4" />;
      case 'silver': return <Shield className="h-4 w-4" />;
      case 'gold': return <Crown className="h-4 w-4" />;
      default: return <Zap className="h-4 w-4" />;
    }
  };

  const getPlanColor = (planType) => {
    switch (planType) {
      case 'free': return 'bg-gray-100 text-gray-800';
      case 'bronze': return 'bg-orange-100 text-orange-800';
      case 'silver': return 'bg-gray-200 text-gray-900';
      case 'gold': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatNumber = (num) => {
    if (num === -1) return '∞';
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="space-y-3">
              <div className="h-3 bg-gray-200 rounded"></div>
              <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !planData) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
            <p>{error || 'Failed to load plan information'}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Current Plan</CardTitle>
          <Badge className={getPlanColor(planData.plan.type)}>
            <div className="flex items-center gap-1">
              {getPlanIcon(planData.plan.type)}
              {planData.plan.name}
            </div>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* API Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">API Calls</span>
            <span className={`text-sm font-medium ${getUsageColor(planData.usage.api_calls.percentage)}`}>
              {formatNumber(planData.usage.api_calls.used)} / {formatNumber(planData.usage.api_calls.limit)}
            </span>
          </div>
          {!planData.usage.api_calls.unlimited && (
            <Progress 
              value={Math.min(100, planData.usage.api_calls.percentage)} 
              className="h-2"
            />
          )}
        </div>

        {/* Resources Usage */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600">Screeners</span>
              <span className="text-xs font-medium">
                {planData.usage.resources.screeners.used} / {formatNumber(planData.usage.resources.screeners.limit)}
              </span>
            </div>
            {!planData.usage.resources.screeners.unlimited && (
              <Progress 
                value={Math.min(100, planData.usage.resources.screeners.percentage)} 
                className="h-1"
              />
            )}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600">Watchlists</span>
              <span className="text-xs font-medium">
                {planData.usage.resources.watchlists.used} / {formatNumber(planData.usage.resources.watchlists.limit)}
              </span>
            </div>
            {!planData.usage.resources.watchlists.unlimited && (
              <Progress 
                value={Math.min(100, planData.usage.resources.watchlists.percentage)} 
                className="h-1"
              />
            )}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600">Portfolios</span>
              <span className="text-xs font-medium">
                {planData.usage.resources.portfolios.used} / {formatNumber(planData.usage.resources.portfolios.limit)}
              </span>
            </div>
            {!planData.usage.resources.portfolios.unlimited && (
              <Progress 
                value={Math.min(100, planData.usage.resources.portfolios.percentage)} 
                className="h-1"
              />
            )}
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600">Alerts</span>
              <span className="text-xs font-medium">
                {planData.usage.resources.alerts.used} / {formatNumber(planData.usage.resources.alerts.limit)}
              </span>
            </div>
            {!planData.usage.resources.alerts.unlimited && (
              <Progress 
                value={Math.min(100, planData.usage.resources.alerts.percentage)} 
                className="h-1"
              />
            )}
          </div>
        </div>

        {/* Recommendations */}
        {planData.recommendations && planData.recommendations.length > 0 && (
          <div className="space-y-2">
            {planData.recommendations.map((rec, index) => (
              <div key={index} className={`p-3 rounded-lg ${
                rec.type === 'upgrade_required' ? 'bg-red-50 border border-red-200' :
                rec.type === 'upgrade_warning' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-blue-50 border border-blue-200'
              }`}>
                <div className="flex items-start gap-2">
                  <AlertTriangle className={`h-4 w-4 mt-0.5 ${
                    rec.type === 'upgrade_required' ? 'text-red-500' :
                    rec.type === 'upgrade_warning' ? 'text-yellow-500' :
                    'text-blue-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{rec.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{rec.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Upgrade Button */}
        {planData.plan.type !== 'gold' && (
          <div className="pt-2">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => window.location.href = '/pricing'}
            >
              Upgrade Plan
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlanUsage;