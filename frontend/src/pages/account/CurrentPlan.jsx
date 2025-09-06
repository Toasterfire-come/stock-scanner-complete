import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Progress } from "../../components/ui/progress";
import { Skeleton } from "../../components/ui/skeleton";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { 
  Crown, 
  Zap, 
  ArrowUpCircle, 
  Calendar, 
  CreditCard,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Bell,
  Shield,
  Users,
  Rocket
} from "lucide-react";
import { getCurrentPlan, changePlan } from "../../api/client";

const CurrentPlan = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [planData, setPlanData] = useState(null);
  const [isChangingPlan, setIsChangingPlan] = useState(false);

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const response = await getCurrentPlan();
        if (response.success) {
          setPlanData(response.data);
        } else {
          // Mock data for demo
          setPlanData({
            plan_name: "Professional",
            plan_type: "pro",
            is_premium: true,
            billing_cycle: "monthly",
            next_billing_date: "2024-04-15T00:00:00Z",
            features: {
              api_calls_limit: 10000,
              real_time_data: true,
              advanced_screening: true,
              portfolio_analytics: true,
              premium_support: true
            }
          });
        }
      } catch (error) {
        console.error("Failed to load plan data:", error);
        setPlanData({
          plan_name: "Free",
          plan_type: "free",
          is_premium: false,
          billing_cycle: null,
          next_billing_date: null,
          features: {
            api_calls_limit: 1000,
            real_time_data: false,
            advanced_screening: false,
            portfolio_analytics: false,
            premium_support: false
          }
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlan();
  }, []);

  const handlePlanChange = async (newPlanType, billingCycle) => {
    setIsChangingPlan(true);
    try {
      const response = await changePlan({
        plan_type: newPlanType,
        billing_cycle: billingCycle
      });

      if (response.success) {
        toast.success("Plan updated successfully!");
        setPlanData(prev => ({
          ...prev,
          plan_type: newPlanType,
          billing_cycle: billingCycle,
          is_premium: newPlanType !== "free"
        }));
      } else {
        toast.error("Failed to update plan");
      }
    } catch (error) {
      toast.error("Failed to update plan");
    } finally {
      setIsChangingPlan(false);
    }
  };

  const getPlanIcon = (planType) => {
    switch (planType) {
      case 'pro':
      case 'professional':
        return <Crown className="h-6 w-6 text-blue-500" />;
      case 'enterprise':
        return <Rocket className="h-6 w-6 text-purple-500" />;
      default:
        return <Zap className="h-6 w-6 text-gray-500" />;
    }
  };

  const getPlanColor = (planType) => {
    switch (planType) {
      case 'pro':
      case 'professional':
        return 'blue';
      case 'enterprise':
        return 'purple';
      default:
        return 'gray';
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid lg:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <Skeleton className="h-8 w-8 mb-4" />
                <Skeleton className="h-6 w-32 mb-2" />
                <Skeleton className="h-4 w-24" />
              </CardContent>
            </Card>
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-32" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="flex items-center justify-between">
                        <Skeleton className="h-4 w-48" />
                        <Skeleton className="h-4 w-16" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const usagePercentage = planData.features.api_calls_limit 
    ? Math.min((850 / planData.features.api_calls_limit) * 100, 100)
    : 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Current Plan</h1>
          <p className="text-gray-600 mt-2">
            Manage your subscription and explore available features
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Plan Overview */}
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  {getPlanIcon(planData.plan_type)}
                </div>
                <h3 className="text-xl font-semibold mb-2">{planData.plan_name}</h3>
                {planData.is_premium ? (
                  <Badge className="bg-yellow-100 text-yellow-800 mb-4">
                    <Crown className="h-3 w-3 mr-1" />
                    Premium
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="mb-4">
                    Free Plan
                  </Badge>
                )}

                {planData.next_billing_date && (
                  <div className="text-sm text-gray-600 mb-4">
                    <Calendar className="h-4 w-4 inline mr-1" />
                    Next billing: {new Date(planData.next_billing_date).toLocaleDateString()}
                  </div>
                )}

                <div className="space-y-2">
                  <Button asChild className="w-full">
                    <Link to="/pricing">
                      <ArrowUpCircle className="h-4 w-4 mr-2" />
                      {planData.is_premium ? "Manage Plan" : "Upgrade Plan"}  
                    </Link>
                  </Button>
                  
                  <Button asChild variant="outline" className="w-full">
                    <Link to="/account/billing">
                      <CreditCard className="h-4 w-4 mr-2" />
                      Billing History
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Plan Features */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Plan Features</CardTitle>
                <CardDescription>
                  Features included in your current plan
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <BarChart3 className="h-5 w-5 text-blue-500 mr-3" />
                      <span>Real-time Market Data</span>
                    </div>
                    {planData.features.real_time_data ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Badge variant="secondary">Premium</Badge>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <TrendingUp className="h-5 w-5 text-blue-500 mr-3" />
                      <span>Advanced Screening</span>
                    </div>
                    {planData.features.advanced_screening ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Badge variant="secondary">Premium</Badge>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Bell className="h-5 w-5 text-blue-500 mr-3" />
                      <span>Portfolio Analytics</span>
                    </div>
                    {planData.features.portfolio_analytics ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Badge variant="secondary">Premium</Badge>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Shield className="h-5 w-5 text-blue-500 mr-3" />
                      <span>Premium Support</span>
                    </div>
                    {planData.features.premium_support ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Badge variant="secondary">Premium</Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Usage Statistics</CardTitle>
                <CardDescription>
                  Your current usage this month
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">API Calls</span>
                    <span className="text-sm text-gray-600">
                      850 / {planData.features.api_calls_limit?.toLocaleString() || 'Unlimited'}
                    </span>
                  </div>
                  <Progress value={usagePercentage} className="h-2" />
                  {usagePercentage > 80 && (
                    <Alert className="mt-2">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        You're approaching your monthly API limit. Consider upgrading your plan.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">12</div>
                    <div className="text-sm text-blue-600">Active Screeners</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">47</div>
                    <div className="text-sm text-green-600">Watchlist Items</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Plan Options */}
            {!planData.is_premium && (
              <Card>
                <CardHeader>
                  <CardTitle>Upgrade Options</CardTitle>
                  <CardDescription>
                    Quick upgrade to unlock premium features
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3">
                    <Button
                      onClick={() => handlePlanChange("pro", "monthly")}
                      disabled={isChangingPlan}
                      className="justify-between"
                    >
                      <span className="flex items-center">
                        <Crown className="h-4 w-4 mr-2" />
                        Professional Monthly
                      </span>
                      <span>$29/month</span>
                    </Button>
                    
                    <Button
                      variant="outline"
                      onClick={() => handlePlanChange("pro", "annual")}
                      disabled={isChangingPlan}
                      className="justify-between"
                    >
                      <span className="flex items-center">
                        <Crown className="h-4 w-4 mr-2" />
                        Professional Annual
                      </span>
                      <span className="text-green-600">
                        $290/year <small className="text-xs">(Save $58)</small>
                      </span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentPlan;