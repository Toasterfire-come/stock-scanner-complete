import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
 
import {
  CheckCircle,
  X,
  Shield,
  Rocket,
  Star,
  BarChart3,
  ArrowRight,
  Gift,
  Mail
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "../context/SecureAuthContext";
import { changePlan, initializeDiscountCodes, createPayPalOrder, validateDiscountCode } from "../api/client";

const PricingPro = () => {
  const [isAnnual, setIsAnnual] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, updateUser } = useAuth();

  const fromSignup = location.state?.fromSignup;
  const preSelectedPlan = location.state?.selectedPlan;

  useEffect(() => {
    (async () => { try { await initializeDiscountCodes(); } catch {} })();
    if (preSelectedPlan) {
      const plan = plans.find(p => p.name.toLowerCase() === preSelectedPlan);
      if (plan) {
        setSelectedPlan({ ...plan, billingCycle: 'monthly' });
      }
    }
  }, [preSelectedPlan]);

  const plans = [
    {
      name: "Bronze",
      description: "Perfect for individual traders getting started",
      // icon removed from header to satisfy 'plan icon in the corner' removal
      price: { monthly: 24.99, annual: 299.99 },
      popular: false,
      features: [
        { name: "150 API calls per day, 1500/month", included: true },
        { name: "Real-time stock data", included: true },
        { name: "Basic stock screener", included: true },
        { name: "Email alerts & notifications", included: true },
        { name: "Real-time alerts", included: true },
        { name: "Portfolio tracking (5 positions)", included: true },
      ],
      limits: {
        apiCalls: "100/day, 1500/month",
        portfolios: "1 portfolio",
        watchlists: "3 watchlists",
        alerts: "25 alerts"
      }
    },
    {
      name: "Silver",
      description: "Advanced tools for serious traders",
      price: { monthly: 49.99, annual: 599.99 },
      popular: false,
      features: [
        { name: "500 API calls per day, 5000/month", included: true },
        { name: "Advanced stock screener", included: true },
        { name: "Priority email support", included: true },
        { name: "Custom watchlists (10)", included: true },
      ],
      limits: {
        apiCalls: "500/day, 5000/month",
        portfolios: "5 portfolios",
        watchlists: "10 watchlists",
        alerts: "50 alerts"
      }
    },
    {
      name: "Gold",
      description: "Ultimate trading experience for professionals",
      price: { monthly: 79.99, annual: 959.99 },
      popular: false,
      features: [
        { name: "Unlimited API calls", included: true },
        { name: "Premium stock screener", included: true },
        { name: "Full REST API access", included: true },
      ],
      limits: {
        apiCalls: "Unlimited",
        portfolios: "Unlimited",
        watchlists: "Unlimited",
        alerts: "Unlimited"
      }
    },
    {
      name: "Free",
      description: "Perfect for getting started with trading",
      price: { monthly: 0, annual: 0 },
      popular: false,
      isFree: true,
      features: [
        { name: "15 API calls per month", included: true },
        { name: "Basic stock screening", included: true },
      ],
      limits: {
        apiCalls: "15/month",
        portfolios: "1 portfolio",
        watchlists: "0 watchlists",
        alerts: "0 alerts"
      }
    }
  ];

  const handlePlanSelect = (plan, billingCycle) => {
    setSelectedPlan({ ...plan, billingCycle });
  };

  const continueToCheckout = async (plan) => {
    try {
      try { await initializeDiscountCodes(); } catch {}
      const code = 'TRIAL';
      try { await validateDiscountCode(code); } catch {}
      const cycle = isAnnual ? 'annual' : 'monthly';
      const res = await createPayPalOrder(plan.name.toLowerCase(), cycle, code);
      if (res?.approval_url) {
        window.location.href = res.approval_url;
      } else {
        toast.error('Failed to start checkout');
      }
    } catch (e) {
      toast.error('Checkout unavailable right now');
    }
  };

  const calculateSavings = (plan) => {
    const monthlyCost = plan.price.monthly * 12;
    const annualCost = plan.price.annual;
    return Math.round(((monthlyCost - annualCost) / monthlyCost) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          {/* TRIAL Banner */}
          <div className="mb-6">
            <div className="inline-flex items-center bg-yellow-100 text-yellow-800 px-6 py-3 rounded-full font-medium text-base border border-yellow-200">
              <Gift className="h-5 w-5 mr-2" />
              Use code TRIAL for a 7‑day $1 trial on paid plans · Use code REF50 for 50% off first month
            </div>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">Choose Your Trading Edge</h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Join thousands of traders using our tools to make better trading decisions and improve their market analysis.
          </p>
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-lg font-medium ${!isAnnual ? 'text-blue-600' : 'text-gray-500'}`}>Monthly</span>
            <Switch checked={isAnnual} onCheckedChange={setIsAnnual} className="data-[state=checked]:bg-blue-600" />
            <span className={`text-lg font-medium ${isAnnual ? 'text-blue-600' : 'text-gray-500'}`}>Annual</span>
            {isAnnual && (
              <Badge variant="secondary" className="bg-green-100 text-green-800 ml-2">Save up to 25%</Badge>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-4 gap-8 mb-16">
          {plans.map((plan) => {
            const currentPrice = isAnnual ? plan.price.annual : plan.price.monthly;
            const savings = calculateSavings(plan);
            return (
              <Card key={plan.name} className={`relative hover:shadow-2xl transition-all duration-300`}>
                {/* Remove corner/overlay badges and plan icons */}
                <CardHeader className={`rounded-t-lg p-8`}>
                  {/* Title & Desc */}
                  <CardTitle className="text-2xl font-bold text-center mb-2">{plan.name}</CardTitle>
                  <p className="text-center text-gray-600 mb-6">{plan.description}</p>
                  <div className="text-center">
                    {plan.isFree ? (
                      <div className="flex items-baseline justify-center">
                        <span className="text-4xl font-bold">$0</span>
                        <span className="text-lg ml-1">/forever</span>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-baseline justify-center">
                          <span className="text-4xl font-bold">${isAnnual ? Math.round(currentPrice / 12) : currentPrice}</span>
                          <span className="text-lg ml-1">/{isAnnual ? 'mo' : 'month'}</span>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">Auto‑renews {isAnnual ? 'annually' : 'monthly'}. Cancel anytime.</div>
                        {isAnnual && (
                          <div className="mt-2">
                            <span className="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-200">Billed ${currentPrice} annually (Save {savings}%)</span>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="p-8 space-y-6">
                  {/* Usage Limits - improved styling */}
                  <div className="bg-white p-4 rounded-lg border">
                    <h4 className="font-semibold mb-3 text-gray-900">Usage Limits</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                      <div className="flex flex-col">
                        <span className="text-gray-500">API Calls</span>
                        <span className="font-medium text-gray-900">{plan.limits.apiCalls}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-500">Alerts</span>
                        <span className="font-medium text-gray-900">{plan.limits.alerts}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-500">Portfolios</span>
                        <span className="font-medium text-gray-900">{plan.limits.portfolios}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-gray-500">Watchlists</span>
                        <span className="font-medium text-gray-900">{plan.limits.watchlists}</span>
                      </div>
                    </div>
                  </div>

                  {/* Features List */}
                  <div className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center space-x-3">
                        {feature.included ? (
                          <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                        ) : (
                          <X className="h-5 w-5 text-gray-300 flex-shrink-0" />
                        )}
                        <span className={`text-sm ${feature.included ? 'text-gray-900' : 'text-gray-400'}`}>{feature.name}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <div className="space-y-3 pt-2">
                    <Button className="w-full text-lg py-6" onClick={() => continueToCheckout(plan)}>
                      {plan.isFree ? "Try Now for Free" : "Try Today for $1"}
                      <ArrowRight className="h-5 w-5 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Additional Features (minimal and production safe) */}
        <div className="bg-white rounded-2xl p-10 mb-16 shadow-xl">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-10">Why Choose Trade Scan Pro?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[{icon: Shield, title: 'Secure Platform', desc: 'Industry-standard security and data protection'},
              {icon: Rocket, title: 'Fast & Reliable', desc: 'Consistent uptime and performance'},
              {icon: Star, title: 'Trader Approved', desc: 'Trusted by traders worldwide'},
              {icon: BarChart3, title: 'Market Focused', desc: 'NYSE-focused insights'}].map((f, i) => {
              const Icon = f.icon;
              return (
                <div key={i} className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-blue-600">
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
                  <p className="text-gray-600 text-sm">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Enterprise CTA */}
        <Card className="bg-gradient-to-r from-gray-900 to-gray-800 text-white">
          <CardContent className="p-10 text-center">
            <h2 className="text-3xl font-bold mb-3">Need a Custom Solution?</h2>
            <p className="text-lg text-gray-300 mb-6 max-w-2xl mx-auto">Enterprise plans with custom API limits, dedicated support, and tailored solutions available.</p>
            <Button variant="secondary" size="lg" className="text-lg px-8 py-4">
              <Mail className="h-5 w-5 mr-2" />
              Contact Sales
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PricingPro;