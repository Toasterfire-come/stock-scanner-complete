import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/SecureAuthContext";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Check, Crown, Zap, Star, Gift, ArrowRight } from "lucide-react";

const plans = [
  {
    id: "bronze",
    name: "Bronze",
    price: "$24.99",
    period: "month",
    trialPrice: "$1",
    description: "Great for individual traders",
    features: [
      "150 API calls per day, 1500/month",
      "Unlimited scanner combinations",
      "Advanced screening tools",
      "Real-time alerts",
      "Email support",
      "2 Watchlists",
      "No portfolios"
    ],
    limits: {
      api_calls: 1500,
      screeners: 10,
      alerts: 50,
      watchlists: 2,
      portfolios: 0,
    },
    icon: Zap,
    color: "orange",
    popular: true,
  },
  {
    id: "silver",
    name: "Silver",
    price: "$49.99",
    period: "month",
    trialPrice: "$1",
    description: "Perfect for professional traders",
    features: [
      "500 API calls per day, 5000/month",
      "Unlimited scanner combinations",
      "All screening tools",
      "Custom alerts & notifications (100 alerts)",
      "10 Watchlists",
      "1 Portfolio",
      "Priority support",
      "Advanced analytics"
    ],
    limits: {
      api_calls: 5000,
      screeners: 20,
      alerts: 100,
      watchlists: 10,
      portfolios: 1,
    },
    icon: Crown,
    color: "blue",
  },
  {
    id: "gold",
    name: "Gold",
    price: "$89.99",
    period: "month",
    trialPrice: "$1",
    description: "For trading teams and institutions",
    features: [
      "Unlimited API calls",
      "Unlimited daily calls",
      "All premium features",
      "Custom integrations",
      "Dedicated support",
      "Team collaboration",
      "Advanced analytics & reporting"
    ],
    limits: {
      api_calls: -1,
      screeners: -1,
      alerts: -1,
      watchlists: -1,
      portfolios: -1,
    },
    icon: Crown,
    color: "yellow",
  },
  {
    id: "free",
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "15 API calls per month",
      "Unlimited scanner combinations",
      "Basic stock screening",
      "Community support",
      "Basic portfolio tracking",
      "0 Watchlists",
      "1 Portfolio"
    ],
    limitations: [
      "No email alerts",
      "No watchlists"
    ],
    limits: {
      api_calls: 30,
      screeners: 1,
      alerts: 0,
      watchlists: 0,
      portfolios: 1,
    },
    icon: Star,
    color: "gray",
    isFree: true,
  },
];

export default function PlanSelection() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, updateUser } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState("bronze");
  const [isAnnual, setIsAnnual] = useState(false);

  // 15% annual discount rounded to nearest price ending in 9.99
  const roundToNearest9_99 = (value) => {
    if (!value || value <= 0) return 0;
    const base = Math.floor(value / 10) * 10 + 9.99;
    const higher = base + 10;
    return Number((Math.abs(value - base) <= Math.abs(higher - value) ? base : higher).toFixed(2));
  };
  const computeAnnual = (monthly) => roundToNearest9_99(parseFloat(String(monthly).replace('$','')) * 12 * 0.85);
  const [isLoading, setIsLoading] = useState(false);

  // Check if this is from the signup flow
  const isNewUser = location.state?.newUser;
  const userEmail = location.state?.email;
  const referral = location.state?.ref;

  const handlePlanSelect = async (planId) => {
    setIsLoading(true);
    
    try {
      if (planId === "free") {
        // Keep user on free plan and go to app
        updateUser({ plan: 'free' });
        navigate('/app/dashboard', { replace: true });
        return;
      }

      // For paid plans, send to pricing page to choose cycle and checkout
      navigate('/pricing', { 
        state: { 
          fromSignup: true, 
          selectedPlan: planId,
          userEmail: userEmail,
          discount_code: referral ? `REF_${String(referral).toUpperCase()}` : undefined
        } 
      });
    } catch (error) {
      console.error("Plan selection error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 sm:py-12 px-4">
      <div className="max-w-screen-2xl mx-auto px-2 sm:px-4 lg:px-8">
        <div className="text-center mb-8 sm:mb-12">
          {isNewUser && (
            <Badge className="mb-4 bg-green-100 text-green-800 px-4 py-2">
              <Gift className="h-4 w-4 mr-2" />
              Welcome! Account created successfully
            </Badge>
          )}
          
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
            Choose Your Trading Plan
          </h1>
          <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
            Select the perfect plan for your trading needs. All paid plans include a 7-day trial for just $1.
          </p>
        </div>

        {/* Updated TRIAL Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-6 py-3 rounded-full font-bold text-base">
            <Zap className="h-5 w-5 mr-2" />
            Use code TRIAL for a 7‑day 1$ trial on paid plans
          </div>
        </div>

        {/* Billing Toggle */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <span className={!isAnnual ? "font-semibold" : "text-gray-600"}>Monthly</span>
          <button
            type="button"
            className={`relative inline-flex h-6 w-11 items-center rounded-full ${isAnnual ? 'bg-blue-600' : 'bg-gray-200'}`}
            onClick={() => setIsAnnual((v) => !v)}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${isAnnual ? 'translate-x-6' : 'translate-x-1'}`}
            />
          </button>
          <span className={isAnnual ? "font-semibold" : "text-gray-600"}>Annual</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-4 gap-8 lg:gap-12 xl:gap-16 2xl:gap-20">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const isSelected = selectedPlan === plan.id;
            
            return (
              <Card 
                key={plan.id} 
                className={`relative h-full flex flex-col cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  isSelected ? "ring-2 ring-blue-500 shadow-lg" : ""
                } ${plan.popular ? "border-orange-200 scale-105" : ""} ${plan.isFree ? "order-last lg:order-none" : ""}`}
                onClick={() => setSelectedPlan(plan.id)}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-orange-500 text-white px-4 py-1">
                    Most Popular
                  </Badge>
                )}
                
                <CardHeader className="text-center pb-4 lg:pb-6">
                  <div className={`w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center ${
                    plan.color === "gray" ? "bg-gray-100" :
                    plan.color === "orange" ? "bg-orange-100" :
                    plan.color === "blue" ? "bg-blue-100" : "bg-yellow-100"
                  }`}>
                    <Icon className={`w-6 h-6 ${
                      plan.color === "gray" ? "text-gray-600" :
                      plan.color === "orange" ? "text-orange-600" :
                      plan.color === "blue" ? "text-blue-600" : "text-yellow-600"
                    }`} />
                  </div>
                  
                  <CardTitle className="text-xl sm:text-2xl">{plan.name}</CardTitle>
                  
                  <div className="space-y-2">
                    {!plan.isFree && (
                      <div className="text-lg font-bold text-blue-600">
                        TRIAL: {plan.trialPrice} for 7 days
                      </div>
                    )}
                    <div className="text-2xl sm:text-3xl font-bold text-gray-900">
                      {(() => {
                        const monthly = parseFloat(String(plan.price).replace('$',''));
                        const annual = computeAnnual(monthly);
                        const display = isAnnual ? `$${annual.toFixed(2)}` : plan.price;
                        return (
                          <>
                            {display}
                            <span className="text-sm font-normal text-gray-500">/{isAnnual ? 'year' : plan.period}</span>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                  
                  <CardDescription className="text-sm sm:text-base">{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4 lg:space-y-6 flex-grow">
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className={`flex items-start ${index > 2 ? 'hidden sm:flex' : ''}`}>
                        <Check className="w-4 h-4 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Limits Summary */}
                  {plan.limits && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-700">
                        <div>
                          <span className="text-gray-600">API Calls:</span>
                          <span className="font-medium ml-1">{plan.limits.api_calls === -1 ? 'Unlimited' : plan.limits.api_calls.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Screeners:</span>
                          <span className="font-medium ml-1">{plan.limits.screeners === -1 ? 'Unlimited' : plan.limits.screeners.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Alerts:</span>
                          <span className="font-medium ml-1">{plan.limits.alerts === -1 ? 'Unlimited' : plan.limits.alerts.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Watchlists:</span>
                          <span className="font-medium ml-1">{plan.limits.watchlists === -1 ? 'Unlimited' : plan.limits.watchlists.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Portfolios:</span>
                          <span className="font-medium ml-1">{plan.limits.portfolios === -1 ? 'Unlimited' : plan.limits.portfolios.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {plan.limitations && plan.limitations.length > 0 && (
                    <div className="border-t pt-3">
                      <p className="text-xs text-gray-500 mb-2">Limitations:</p>
                      <ul className="space-y-1">
                        {plan.limitations.map((limitation, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-xs text-gray-400 mr-2">•</span>
                            <span className="text-xs text-gray-500">{limitation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <Button
                    className={`w-full mt-6 h-11 sm:h-12 text-base ${
                      isSelected 
                        ? "bg-blue-600 hover:bg-blue-700" 
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePlanSelect(plan.id);
                    }}
                    disabled={isLoading}
                  >
                    {plan.isFree ? "Get Started Free" : "Try for $1"}
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                  
                  {!plan.isFree && (
                    <p className="text-xs text-gray-500 text-center">
                      TRIAL: 7-day trial for $1 then {plan.price}/{plan.period}
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="text-center mt-8 sm:mt-12 space-y-4">
          {/* Removed extra payment button for simplified flow */}
          
          <p className="text-sm text-gray-500">
            You can change your plan anytime from your account settings
          </p>
          
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-600">
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Cancel anytime
            </div>
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              No setup fees
            </div>
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Email support
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}