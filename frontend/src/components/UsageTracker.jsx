import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { AlertTriangle, Zap, TrendingUp } from "lucide-react";
import { useAuth } from "../context/SecureAuthContext";
import { getCurrentApiUsage, getPlanLimits, getStoredUserPlan, getUsageSummary } from "../api/client";

const UsageTracker = () => {
  const { user, isAuthenticated } = useAuth();
  const [usage, setUsage] = useState(0);
  const [limits, setLimits] = useState(null);
  const [plan, setPlan] = useState('free');

  useEffect(() => {
    let mounted = true;
    (async () => {
      if (!isAuthenticated) return;
      const currentUsage = getCurrentApiUsage();
      const planLimits = getPlanLimits();
      const userPlan = getStoredUserPlan();
      try {
        const res = await getUsageSummary();
        // If server returns category counts/limits, prefer them
        const cats = res?.data?.categories;
        if (mounted && cats) {
          // Attach to limits for UI elsewhere if needed
          planLimits._serverCategories = cats;
        }
      } catch {}
      if (!mounted) return;
      setUsage(currentUsage);
      setLimits(planLimits);
      setPlan(userPlan);
    })();
    return () => { mounted = false; };
  }, [isAuthenticated, user]);

  if (!isAuthenticated || !limits) {
    return null;
  }

  const usagePercentage = limits.monthlyApi === Infinity 
    ? 0 
    : Math.min((usage / limits.monthlyApi) * 100, 100);

  const isNearLimit = usagePercentage > 80;
  const isOverLimit = usagePercentage >= 100;

  return (
    <Card className={`${isOverLimit ? 'border-red-500' : isNearLimit ? 'border-yellow-500' : ''}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">API Usage</CardTitle>
        <div className="flex items-center space-x-2">
          {isOverLimit && <AlertTriangle className="h-4 w-4 text-red-500" />}
          {isNearLimit && !isOverLimit && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
          <Zap className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold mb-2">
          {usage.toLocaleString()} 
          {limits.monthlyApi !== Infinity && (
            <span className="text-sm text-muted-foreground font-normal">
              / {limits.monthlyApi.toLocaleString()}
            </span>
          )}
        </div>
        
        {limits.monthlyApi !== Infinity ? (
          <>
            <Progress 
              value={usagePercentage} 
              className={`w-full mb-2 ${
                isOverLimit ? 'bg-red-100' : 
                isNearLimit ? 'bg-yellow-100' : 
                'bg-gray-100'
              }`} 
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                {limits.monthlyApi - usage > 0 ? 
                  `${(limits.monthlyApi - usage).toLocaleString()} calls remaining` :
                  'Limit exceeded'
                }
              </p>
              <Badge 
                variant={isOverLimit ? 'destructive' : isNearLimit ? 'default' : 'secondary'}
                className="text-xs"
              >
                {usagePercentage.toFixed(1)}%
              </Badge>
            </div>
          </>
        ) : (
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              <TrendingUp className="h-3 w-3 mr-1" />
              Unlimited
            </Badge>
            <p className="text-xs text-muted-foreground">
              {plan.charAt(0).toUpperCase() + plan.slice(1)} plan
            </p>
          </div>
        )}

        <div className="text-xs text-muted-foreground mt-2">
          Current month • Resets monthly
        </div>
      </CardContent>
    </Card>
  );
};

export default UsageTracker;