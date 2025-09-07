import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Suspense, lazy } from 'react';
const PayPalCheckout = lazy(() => import("../components/PayPalCheckout"));
import {
  CheckCircle,
  X,
  Zap,
  Crown,
  Shield,
  Rocket,
  Star,
  TrendingUp,
  BarChart3,
  Bell,
  Headphones,
  Clock,
  Globe,
  ArrowRight,
  Gift,
  Mail
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "../context/SecureAuthContext";
import { changePlan } from "../api/client";

const PricingPro = () => {
  const [isAnnual, setIsAnnual] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, updateUser } = useAuth();

  // Check if coming from signup flow
  const fromSignup = location.state?.fromSignup;
  const preSelectedPlan = location.state?.selectedPlan;

  useEffect(() => {
    if (preSelectedPlan) {
      const plan = plans.find(p => p.name.toLowerCase() === preSelectedPlan);
      if (plan) {
        setSelectedPlan({ ...plan, billingCycle: 'monthly' });
        setShowCheckout(true);
      }
    }
  }, [preSelectedPlan]);

  const plans = [
    {
      name: "Bronze",
      description: "Perfect for individual traders getting started",
      icon: <BarChart3 className="h-8 w-8" />,
      color: "border-orange-200 bg-orange-50",
      headerColor: "bg-gradient-to-r from-orange-500 to-orange-600",
      price: { monthly: 24.99, annual: 249.99 },
      popular: true,
      features: [
        { name: "1,500 API calls per month", included: true },
        { name: "50 API calls per day", included: true },
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
        apiCalls: "1,500/month, 50/day",
        portfolios: "1 portfolio",
        watchlists: "3 watchlists",
        alerts: "25 alerts"
      }
    },
    {
      name: "Silver",
      description: "Advanced tools for serious traders",
      icon: <Crown className="h-8 w-8" />,
      color: "border-gray-300 bg-gray-50",
      headerColor: "bg-gradient-to-r from-gray-400 to-gray-500",
      price: { monthly: 39.99, annual: 399.99 },
      popular: false,
      features: [
        { name: "5,000 API calls per month", included: true },
        { name: "250 API calls per day", included: true },
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
        apiCalls: "5,000/month, 250/day",
        portfolios: "Unlimited",
        watchlists: "10 watchlists",
        alerts: "100 alerts"
      }
    },
    {
      name: "Gold",
      description: "Ultimate trading experience for professionals",
      icon: <Rocket className="h-8 w-8" />,
      color: "border-yellow-300 bg-yellow-50",
      headerColor: "bg-gradient-to-r from-yellow-500 to-yellow-600",
      price: { monthly: 89.99, annual: 899.99 },
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
    },
    {
      name: "Free",
      description: "Perfect for getting started with trading",
      icon: <Star className="h-8 w-8" />,
      color: "border-gray-200 bg-gray-50",
      headerColor: "bg-gradient-to-r from-gray-500 to-gray-600",
      price: { monthly: 0, annual: 0 },
      popular: false,
      isFree: true,
      features: [
        { name: "50 API calls per month", included: true },
        { name: "Unlimited daily calls", included: true },
        { name: "Basic stock screening", included: true },
        { name: "Email alerts", included: true },
        { name: "Community support", included: true },
        { name: "Basic portfolio tracking", included: true },
        { name: "Advanced screener filters", included: false },
        { name: "Custom watchlists", included: false },
        { name: "API access", included: false },
        { name: "Priority support", included: false }
      ],
      limits: {
        apiCalls: "50/month, unlimited daily",
        portfolios: "1 portfolio",
        watchlists: "3 watchlists",  
        alerts: "5 alerts"
      }
    }
  ];

  const additionalFeatures = [
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Secure Platform",
      description: "Industry-standard security and data protection"
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "NYSE Focus",
      description: "Comprehensive coverage of NYSE-listed stocks"
    },
    {
      icon: <Clock className="h-6 w-6" />,
      title: "Reliable Service",
      description: "Consistent uptime and performance monitoring"
    },
    {
      icon: <Mail className="h-6 w-6" />,
      title: "Email Support",
      description: "Responsive email support for all plans"
    }
  ];

  const handlePlanSelect = (plan, billingCycle) => {
    setSelectedPlan({ ...plan, billingCycle });
    setShowCheckout(true);
  };

  const handlePaymentSuccess = async (paymentData) => {
    try {
      // Update user's plan in the backend
      if (isAuthenticated && selectedPlan) {
        await changePlan({
          plan_type: selectedPlan.name.toLowerCase(),
          billing_cycle: selectedPlan.billingCycle
        });
        // Update local auth state to reflect new plan
        updateUser({ plan: selectedPlan.name.toLowerCase() });
      }

      toast.success("Payment successful! Welcome to Trade Scan Pro!", {
        description: `Your ${selectedPlan.name} plan is now active. Check your email for details.`,
      });
      
      setShowCheckout(false);
      
      // Navigate to success page or dashboard
      navigate("/checkout/success", {
        state: {
          planId: selectedPlan.name.toLowerCase(),
          amount: paymentData.finalAmount || paymentData.amount,
          originalAmount: paymentData.originalAmount,
          discount: paymentData.discountApplied
        }
      });
    } catch (error) {
      console.error("Failed to update plan:", error);
      toast.error("Payment processed but failed to update your plan. Please contact support.");
    }
  };

  const handlePaymentError = (error) => {
    toast.error("Payment failed", {
      description: "Please try again or contact support if the issue persists.",
    });
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
            <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-6 py-3 rounded-full font-bold text-lg">
              <Gift className="h-5 w-5 mr-2" />
              TRIAL: 7-Day Trial for Just $1
            </div>
          </div>
          
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Choose Your Trading Edge
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Join thousands of traders using our tools to make better trading decisions and improve their market analysis.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-lg font-medium ${!isAnnual ? 'text-blue-600' : 'text-gray-500'}`}>
              Monthly
            </span>
            <Switch
              checked={isAnnual}
              onCheckedChange={setIsAnnual}
              className="data-[state=checked]:bg-blue-600"
            />
            <span className={`text-lg font-medium ${isAnnual ? 'text-blue-600' : 'text-gray-500'}`}>
              Annual
            </span>
            {isAnnual && (
              <Badge variant="secondary" className="bg-green-100 text-green-800 ml-2">
                Save up to 25%
              </Badge>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-4 gap-8 mb-16">
          {plans.map((plan, index) => {
            const currentPrice = isAnnual ? plan.price.annual : plan.price.monthly;
            const savings = calculateSavings(plan);
            
            return (
              <Card 
                key={plan.name} 
                className={`relative hover:shadow-2xl transition-all duration-300 ${plan.color} ${
                  plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-0 right-0 flex justify-center">
                    <Badge className="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                      <Star className="h-4 w-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className={`text-white ${plan.headerColor} rounded-t-lg p-8`}>
                  <div className="flex items-center justify-center mb-4">
                    {plan.icon}
                  </div>
                  <CardTitle className="text-2xl font-bold text-center mb-2">
                    {plan.name}
                  </CardTitle>
                  <p className="text-center text-white/90 mb-6">
                    {plan.description}
                  </p>
                  
                  <div className="text-center">
                    {plan.isFree ? (
                      <div className="flex items-baseline justify-center">
                        <span className="text-4xl font-bold">
                          $0
                        </span>
                        <span className="text-lg ml-1">
                          /forever
                        </span>
                      </div>
                    ) : (
                      <>
                        <div className="text-lg font-bold text-blue-600 mb-2">
                          TRIAL: $1 for 7 days
                        </div>
                        <div className="flex items-baseline justify-center">
                          <span className="text-4xl font-bold">
                            ${isAnnual ? Math.round(currentPrice / 12) : currentPrice}
                          </span>
                          <span className="text-lg ml-1">
                            /{isAnnual ? 'mo' : 'month'}
                          </span>
                        </div>
                      </>
                    )}
                    
                    {isAnnual && (
                      <div className="mt-2">
                        <span className="text-sm bg-white/20 px-3 py-1 rounded-full">
                          Billed ${currentPrice} annually (Save {savings}%)
                        </span>
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="p-8 space-y-6">
                  {/* Key Limits */}
                  <div className="bg-white p-4 rounded-lg border">
                    <h4 className="font-semibold mb-3 text-gray-900">Usage Limits:</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">API Calls:</span>
                        <span className="ml-2 font-medium">{plan.limits.apiCalls}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Alerts:</span>
                        <span className="ml-2 font-medium">{plan.limits.alerts}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Portfolios:</span>
                        <span className="ml-2 font-medium">{plan.limits.portfolios}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Watchlists:</span>
                        <span className="ml-2 font-medium">{plan.limits.watchlists}</span>
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
                        <span className={`text-sm ${feature.included ? 'text-gray-900' : 'text-gray-400'}`}>
                          {feature.name}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Buttons */}
                  <div className="space-y-3 pt-4">
                    <Dialog open={showCheckout && selectedPlan?.name === plan.name} onOpenChange={setShowCheckout}>
                      <DialogTrigger asChild>
                        <Button 
                          className="w-full text-lg py-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                          onClick={() => handlePlanSelect(plan, isAnnual ? 'annual' : 'monthly')}
                        >
                          {plan.isFree ? 'Get Started Free' : 'TRIAL: Get Started for $1'}
                          <ArrowRight className="h-5 w-5 ml-2" />
                        </Button>
                      </DialogTrigger>
                      
                      <DialogContent className="max-w-md">
                        <DialogHeader>
                          <DialogTitle>Complete Your Subscription</DialogTitle>
                        </DialogHeader>
                        
                        {selectedPlan && (
                          <Suspense fallback={<div className="py-6 text-center">Loading checkout…</div>}>
                            <PayPalCheckout
                              planType={selectedPlan.name.toLowerCase()}
                              billingCycle={selectedPlan.billingCycle}
                              onSuccess={handlePaymentSuccess}
                              onError={handlePaymentError}
                              onCancel={() => setShowCheckout(false)}
                            />
                          </Suspense>
                        )}
                      </DialogContent>
                    </Dialog>

                    <p className="text-xs text-gray-500 text-center">
                      TRIAL: 7-day trial for $1 • Cancel anytime • No setup fees
                    </p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Additional Features */}
        <div className="bg-white rounded-2xl p-12 mb-16 shadow-xl">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Choose Trade Scan Pro?
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {additionalFeatures.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <div className="text-blue-600">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise CTA */}
        <Card className="bg-gradient-to-r from-gray-900 to-gray-800 text-white">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Need a Custom Solution?</h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Enterprise plans with custom API limits, dedicated support, and tailored solutions available.
            </p>
            <Button variant="secondary" size="lg" className="text-lg px-8 py-4">
              <Mail className="h-5 w-5 mr-2" />
              Contact Sales
            </Button>
          </CardContent>
        </Card>

        {/* FAQ Section */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-2">How does the 7-day trial work?</h3>
                <p className="text-gray-600">
                  Pay just $1 to access your chosen plan for 7 days. After the trial, you'll be charged the regular monthly price unless you cancel.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-2">Can I change plans later?</h3>
                <p className="text-gray-600">
                  Yes! Upgrade or downgrade anytime. Changes take effect immediately, and we'll prorate the billing difference.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-2">What payment methods do you accept?</h3>
                <p className="text-gray-600">
                  We accept all major credit cards and PayPal. All payments are secured with industry-standard encryption.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-2">Is there a refund policy?</h3>
                <p className="text-gray-600">
                  You can cancel anytime during your trial period for just the $1 trial fee. Regular subscriptions can be cancelled anytime to prevent future charges.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPro;