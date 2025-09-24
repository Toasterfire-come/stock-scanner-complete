import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/SecureAuthContext";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Switch } from "../../components/ui/switch";
import { Label } from "../../components/ui/label";
import { Check, Crown, Zap, Star, Gift, ArrowRight } from "lucide-react";
import { PLAN_LIMITS } from "../../api/client";

const plans = [
  {
    id: "bronze",
    name: "Bronze",
    price: { monthly: 24.99, annual: 249.90 },
    trialPrice: "$1",
    description: "Great for individual traders",
    features: [
      "150 API calls per day, 1500/month",
      "Unlimited scanner combinations",
      "Advanced screening tools",
      "Real-time alerts",
      "Email support",
      "Basic portfolio tracking"
    ],
    icon: Zap,
    color: "orange",
    popular: true,
  },
  {
    id: "silver",
    name: "Silver",
    price: { monthly: 49.99, annual: 499.90 },
    trialPrice: "$1",
    description: "Perfect for professional traders",
    features: [
      "500 API calls per day, 5000/month",
      "Unlimited scanner combinations",
      "All screening tools",
      "Custom alerts & notifications (50 alerts)",
      "Portfolio tracking (5 portfolios)",
      "Priority support",
      "Advanced analytics"
    ],
    icon: Crown,
    color: "blue",
  },
  {
    id: "gold",
    name: "Gold",
    price: { monthly: 89.99, annual: 899.90 },
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
    icon: Crown,
    color: "yellow",
  },
  {
    id: "free",
    name: "Free",
    price: { monthly: 0, annual: 0 },
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "15 API calls per month",
      "Unlimited scanner combinations",
      "Basic stock screening",
      "Community support",
      "Basic portfolio tracking"
    ],
    limitations: [
      "No email alerts",
      "No watchlists"
    ],
    icon: Star,
    color: "gray",
    isFree: true,
  },
];

export default function PlanSelection() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, updateUser, isAuthenticated } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState("bronze");
  const [isLoading, setIsLoading] = useState(false);
  const [isAnnual, setIsAnnual] = useState(false);

  // Check if this is from the signup flow
  const isNewUser = location.state?.newUser;
  const userEmail = location.state?.email;

  const handlePlanSelect = async (planId) => {
    setIsLoading(true);
    
    try {
      if (!isAuthenticated) {
        navigate('/auth/sign-up', {
          state: {
            selectedPlan: planId,
            fromPlanSelection: true,
            discountCode: 'TRIAL',
          }
        });
        return;
      }
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
          userEmail: userEmail
        } 
      });
    } catch (error) {
      console.error("Plan selection error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatLimit = (val, singular, plural) => {
    if (val === Infinity) return `Unlimited ${plural}`;
    return `${val} ${val === 1 ? singular : plural}`;
  };

  const getPlanFeatureLines = (planId) => {
    const lim = PLAN_LIMITS[planId] || {};
    const lines = [];
    if (lim.monthlyApi !== undefined) lines.push(lim.monthlyApi === Infinity ? 'Unlimited API calls' : `${lim.monthlyApi} API calls per month`);
    if (lim.watchlists !== undefined) lines.push(formatLimit(lim.watchlists, 'Watchlist', 'Watchlists'));
    if (lim.alerts !== undefined) lines.push(formatLimit(lim.alerts, 'Alert per month', 'Alerts per month'));
    if (lim.screeners !== undefined) lines.push(formatLimit(lim.screeners, 'Screener', 'Screeners'));
    if (lim.portfolios !== undefined) lines.push(`Portfolio tracking (${lim.portfolios === Infinity ? 'unlimited' : lim.portfolios})`);
    return lines;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div className="text-center mb-8 sm:mb-12">
          {isNewUser && (
            <Badge className="mb-4 bg-green-100 text-green-800 px-4 py-2">
              <Gift className="h-4 w-4 mr-2" />
              Welcome! Account created successfully
            </Badge>
          )}
          
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight text-gray-900">
            Choose Your Trading Plan
          </h1>
          <p className="mt-3 text-base sm:text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
            Select the perfect plan for your trading needs. All paid plans include a 7-day trial for just $1.
          </p>
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mt-6">
            <Label htmlFor="billing-toggle" className={!isAnnual ? "font-semibold" : ""}>
              Monthly
            </Label>
            <Switch
              id="billing-toggle"
              checked={isAnnual}
              onCheckedChange={setIsAnnual}
            />
            <Label htmlFor="billing-toggle" className={isAnnual ? "font-semibold" : ""}>
              Annual
              <Badge variant="secondary" className="ml-2">Save 17%</Badge>
            </Label>
          </div>
        </div>

        {/* Updated TRIAL Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-6 py-3 rounded-full font-bold text-base">
            <Zap className="h-5 w-5 mr-2" />
            Use code TRIAL for a 7‑day 1$ trial on paid plans
          </div>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-6 sm:gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const isSelected = selectedPlan === plan.id;
            
            return (
              <Card 
                key={plan.id} 
                className={`relative h-full flex flex-col cursor-pointer transition-shadow duration-200 hover:shadow-md overflow-hidden ${
                  isSelected ? "ring-2 ring-blue-600 shadow" : ""
                } ${plan.popular ? "border-blue-200" : ""} ${
                  plan.id === 'bronze' ? 'lg:order-1' :
                  plan.id === 'silver' ? 'lg:order-2' :
                  plan.id === 'gold' ? 'lg:order-3' : ''
                } ${plan.id === 'free' ? 'order-last lg:order-4 lg:col-start-2' : ''}`}
                onClick={() => setSelectedPlan(plan.id)}
              >
                {plan.popular && (
                  <Badge className="absolute top-2 right-2 rounded-full bg-blue-600 text-white px-3 py-1 text-xs font-semibold shadow">
                    Most popular
                  </Badge>
                )}
                
                <CardHeader className="text-center pb-4 lg:pb-6 pt-8">
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
                  
                  <CardTitle className="text-xl sm:text-2xl break-words">{plan.name}</CardTitle>
                  
                  <div className="space-y-2">
                    {!plan.isFree && (
                      <div className="text-lg font-bold text-blue-600">
                        TRIAL: {plan.trialPrice} for 7 days
                      </div>
                    )}
                    <div className="mt-2 text-2xl sm:text-3xl font-bold text-gray-900 leading-tight">
                      ${isAnnual ? plan.price.annual : plan.price.monthly}
                      {plan.price.monthly > 0 && (
                        <span className="ml-1 text-sm font-normal text-gray-500 block sm:inline">
                          /{isAnnual ? 'year' : 'month'}
                        </span>
                      )}
                    </div>
                    {isAnnual && plan.price.monthly > 0 && (
                      <div className="text-sm text-green-600 mt-1">
                        Save ${(plan.price.monthly * 12 - plan.price.annual).toFixed(2)} per year
                      </div>
                    )}
                  </div>
                  
                  <CardDescription className="text-sm sm:text-base leading-relaxed">{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4 lg:space-y-6 flex-grow">
                  <ul className="mt-6 space-y-3 text-sm text-gray-700">
                    {getPlanFeatureLines(plan.id).map((feature, index) => (
                      <li key={index} className={`flex items-start ${index > 2 ? 'hidden sm:flex' : ''}`}>
                        <Check className="w-4 h-4 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-sm text-gray-700 break-words whitespace-normal">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
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
                    size="lg"
                    variant={plan.isFree ? "outline" : "default"}
                    className="w-full mt-8"
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
                      {`TRIAL: 7-day trial for $1 then $${isAnnual ? plan.price.annual : plan.price.monthly}/${isAnnual ? 'year' : 'month'}`}
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="text-center mt-8 sm:mt-12 space-y-4">
          <p className="text-sm text-gray-500">
            Start with our 7-day trial. Cancel anytime, no hidden fees.
          </p>
          
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-600">
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Trusted by thousands of traders
            </div>
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Secure payments via Credit Card & PayPal
            </div>
            <div className="flex items-center">
              <Check className="h-4 w-4 text-green-500 mr-2" />
              Industry‑standard encryption
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}