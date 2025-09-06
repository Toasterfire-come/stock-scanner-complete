import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { CheckCircle, ArrowRight, Crown, Rocket, BarChart3, Zap } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "../../context/AuthContext";

const PlanSelection = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState(null);
  
  // Get email from signup flow
  const email = location.state?.email || user?.email;

  const plans = [
    {
      id: "free",
      name: "Free",
      description: "Perfect for getting started with basic stock analysis",
      icon: <BarChart3 className="h-8 w-8" />,
      color: "border-gray-200 bg-gray-50",
      headerColor: "bg-gradient-to-r from-gray-500 to-gray-600",
      price: 0,
      popular: false,
      features: [
        { name: "50 API calls per month", included: true },
        { name: "10 API calls per day", included: true },
        { name: "Basic stock data", included: true },
        { name: "Simple stock search", included: true },
        { name: "Basic portfolio tracking (3 positions)", included: true },
        { name: "Community support", included: true },
        { name: "Real-time alerts", included: false },
        { name: "Advanced screener", included: false },
        { name: "Premium support", included: false },
        { name: "API access", included: false }
      ],
      limits: {
        apiCalls: "50/month, 10/day",
        portfolios: "1 portfolio",
        watchlists: "3 watchlists",
        alerts: "5 alerts"
      }
    },
    {
      id: "bronze",
      name: "Bronze",
      description: "Great for individual traders getting serious",
      icon: <Crown className="h-8 w-8" />,
      color: "border-orange-200 bg-orange-50",
      headerColor: "bg-gradient-to-r from-orange-500 to-orange-600",
      price: 24.99,
      popular: true,
      features: [
        { name: "2,000 API calls per month", included: true },
        { name: "100 API calls per day", included: true },
        { name: "Real-time stock data", included: true },
        { name: "Basic stock screener", included: true },
        { name: "Email alerts & notifications", included: true },
        { name: "Real-time alerts", included: true },
        { name: "Portfolio tracking (5 positions)", included: true },
        { name: "Email support", included: true },
        { name: "Advanced screener filters", included: false },
        { name: "Custom watchlists", included: false },
        { name: "API access", included: false },
        { name: "Priority support", included: false }
      ],
      limits: {
        apiCalls: "2,000/month, 100/day",
        portfolios: "1 portfolio",
        watchlists: "3 watchlists",
        alerts: "25 alerts"
      }
    },
    {
      id: "silver",
      name: "Silver",
      description: "Advanced tools for serious traders",
      icon: <Zap className="h-8 w-8" />,
      color: "border-gray-300 bg-gray-50",
      headerColor: "bg-gradient-to-r from-gray-400 to-gray-500",
      price: 39.99,
      popular: false,
      features: [
        { name: "10,000 API calls per month", included: true },
        { name: "500 API calls per day", included: true },
        { name: "Real-time stock data", included: true },
        { name: "Advanced stock screener", included: true },
        { name: "Email alerts", included: true },
        { name: "Real-time alerts", included: true },
        { name: "Portfolio tracking (unlimited)", included: true },
        { name: "Priority email support", included: true },
        { name: "Advanced screener filters", included: true },
        { name: "Custom watchlists (10)", included: true },
        { name: "Basic API access", included: true },
        { name: "Enhanced analytics", included: true }
      ],
      limits: {
        apiCalls: "10,000/month, 500/day",
        portfolios: "Unlimited",
        watchlists: "10 watchlists",
        alerts: "100 alerts"
      }
    },
    {
      id: "gold",
      name: "Gold",
      description: "Ultimate trading experience for professionals",
      icon: <Rocket className="h-8 w-8" />,
      color: "border-yellow-300 bg-yellow-50",
      headerColor: "bg-gradient-to-r from-yellow-500 to-yellow-600",
      price: 89.99,
      popular: false,
      features: [
        { name: "Unlimited API calls", included: true },
        { name: "Real-time stock data", included: true },
        { name: "Premium stock screener", included: true },
        { name: "Multi-channel alerts", included: true },
        { name: "Real-time alerts", included: true },
        { name: "Portfolio tracking (unlimited)", included: true },
        { name: "Priority email support", included: true },
        { name: "All screener filters", included: true },
        { name: "Unlimited watchlists", included: true },
        { name: "Advanced insights", included: true },
        { name: "Full REST API access", included: true },
        { name: "Real-time market data", included: true }
      ],
      limits: {
        apiCalls: "Unlimited",
        portfolios: "Unlimited",
        watchlists: "Unlimited",
        alerts: "Unlimited"
      }
    }
  ];

  const handlePlanSelect = (plan) => {
    if (plan.id === "free") {
      // For free plan, just redirect to dashboard
      toast.success("Welcome to Trade Scan Pro! Your free account is ready.");
      navigate("/app/dashboard");
    } else {
      // For paid plans, redirect to checkout
      navigate("/pricing", { 
        state: { 
          selectedPlan: plan.id,
          fromSignup: true 
        } 
      });
    }
  };

  const handleSkipForNow = () => {
    toast.success("Welcome to Trade Scan Pro! You can upgrade anytime from your dashboard.");
    navigate("/app/dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-12">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Trading Plan
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
            Welcome to Trade Scan Pro{email && `, ${email.split('@')[0]}`}! 
            Select the plan that best fits your trading needs. You can change or upgrade anytime.
          </p>
          
          <Badge className="mb-4 text-lg px-4 py-2 bg-green-100 text-green-800">
            7-Day Trial Available for Paid Plans - Just $1!
          </Badge>
        </div>

        {/* Plan Cards */}
        <div className="grid lg:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
          {plans.map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative hover:shadow-xl transition-all duration-300 ${plan.color} ${
                plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <Badge className="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className={`text-white ${plan.headerColor} rounded-t-lg p-6`}>
                <div className="flex items-center justify-center mb-4">
                  {plan.icon}
                </div>
                <CardTitle className="text-2xl font-bold text-center mb-2">
                  {plan.name}
                </CardTitle>
                <p className="text-center text-white/90 mb-4 text-sm">
                  {plan.description}
                </p>
                
                <div className="text-center">
                  <div className="flex items-baseline justify-center">
                    <span className="text-3xl font-bold">
                      ${plan.price}
                    </span>
                    {plan.price > 0 && (
                      <span className="text-lg ml-1">/month</span>
                    )}
                  </div>
                  
                  {plan.price > 0 && (
                    <div className="mt-2">
                      <span className="text-sm bg-white/20 px-3 py-1 rounded-full">
                        Start with $1 trial
                      </span>
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="p-6 space-y-4">
                {/* Key Limits */}
                <div className="bg-white p-3 rounded-lg border">
                  <h4 className="font-semibold mb-2 text-gray-900 text-sm">Usage Limits:</h4>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-600">API Calls:</span>
                      <span className="font-medium">{plan.limits.apiCalls}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Alerts:</span>
                      <span className="font-medium">{plan.limits.alerts}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Portfolios:</span>
                      <span className="font-medium">{plan.limits.portfolios}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Watchlists:</span>
                      <span className="font-medium">{plan.limits.watchlists}</span>
                    </div>
                  </div>
                </div>

                {/* Top Features */}
                <div className="space-y-2">
                  {plan.features.slice(0, 6).map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center space-x-2">
                      <CheckCircle className={`h-4 w-4 flex-shrink-0 ${
                        feature.included ? 'text-green-500' : 'text-gray-300'
                      }`} />
                      <span className={`text-xs ${
                        feature.included ? 'text-gray-900' : 'text-gray-400'
                      }`}>
                        {feature.name}
                      </span>
                    </div>
                  ))}
                  {plan.features.length > 6 && (
                    <p className="text-xs text-gray-500 mt-2">
                      +{plan.features.length - 6} more features...
                    </p>
                  )}
                </div>

                {/* CTA Button */}
                <div className="pt-4">
                  <Button 
                    className="w-full text-sm py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                    onClick={() => handlePlanSelect(plan)}
                  >
                    {plan.price === 0 ? 'Start Free' : 'Start $1 Trial'}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                  
                  {plan.price > 0 && (
                    <p className="text-xs text-gray-500 text-center mt-2">
                      7-day trial • Cancel anytime • No setup fees
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Skip Option */}
        <div className="text-center">
          <p className="text-gray-600 mb-4">
            Not ready to choose? You can always upgrade later.
          </p>
          <Button 
            variant="outline" 
            onClick={handleSkipForNow}
            className="px-8 py-2"
          >
            Skip for now - Start with Free Plan
          </Button>
        </div>

        {/* Features Comparison */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Why Upgrade from Free?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">More API Calls</h3>
              <p className="text-gray-600 text-sm">
                Get up to unlimited API calls vs 50/month on free plan
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Real-time Data</h3>
              <p className="text-gray-600 text-sm">
                Access live market data and real-time price updates
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Crown className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Advanced Tools</h3>
              <p className="text-gray-600 text-sm">
                Advanced screeners, unlimited portfolios, and priority support
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanSelection;