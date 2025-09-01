import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
import { toast } from "sonner";
import { 
  Check, 
  X, 
  Zap, 
  Crown, 
  Rocket,
  Star,
  ArrowRight,
  CreditCard
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { revenueValidate, revenueApply } from "../api/client";

const Pricing = () => {
  const [isAnnual, setIsAnnual] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [discountCode, setDiscountCode] = useState("");
  const [appliedDiscount, setAppliedDiscount] = useState(null);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const plans = [
    {
      id: "free",
      name: "Free",
      description: "Perfect for getting started",
      price: { monthly: 0, annual: 0 },
      features: [
        "5 stock screens per day",
        "Basic market data",
        "3 watchlists",
        "Email alerts",
        "Community support",
      ],
      limitations: [
        "No real-time data",
        "Limited screening criteria",
        "Basic charts only",
      ],
      popular: false,
      icon: <Zap className="h-6 w-6" />,
      color: "gray",
    },
    {
      id: "pro",
      name: "Professional",
      description: "For serious traders",
      price: { monthly: 29, annual: 290 },
      features: [
        "Unlimited stock screens",
        "Real-time market data",
        "50+ screening criteria",
        "Advanced charting",
        "Portfolio analytics",
        "Price alerts",
        "Email & SMS notifications",
        "Priority support",
      ],
      limitations: [],
      popular: true,
      icon: <Crown className="h-6 w-6" />,
      color: "blue",
    },
    {
      id: "enterprise",
      name: "Enterprise",
      description: "For professional teams",
      price: { monthly: 99, annual: 990 },
      features: [
        "Everything in Professional",
        "Advanced analytics",
        "Custom screening",
        "API access",
        "Team collaboration",
        "White-label options",
        "Dedicated support",
        "Custom integrations",
      ],
      limitations: [],
      popular: false,
      icon: <Rocket className="h-6 w-6" />,
      color: "purple",
    },
  ];

  const handlePlanSelect = async (planId) => {
    if (!isAuthenticated) {
      navigate("/auth/sign-up", { 
        state: { selectedPlan: planId } 
      });
      return;
    }

    if (planId === "free") {
      toast.success("You're already on the free plan!");
      return;
    }

    setIsLoading(true);
    
    try {
      const plan = plans.find(p => p.id === planId);
      const amount = isAnnual ? plan.price.annual : plan.price.monthly;
      
      // Create PayPal checkout
      await createPayPalOrder(planId, amount);
    } catch (error) {
      toast.error("Failed to create checkout session");
    } finally {
      setIsLoading(false);
    }
  };

  const createPayPalOrder = async (planId, amount) => {
    // In a real implementation, this would integrate with PayPal SDK
    // For demo, simulate the process
    const finalAmount = appliedDiscount 
      ? appliedDiscount.final_amount 
      : amount;
      
    toast.success(`Redirecting to PayPal for $${finalAmount} payment...`);
    
    // Simulate redirect to PayPal
    setTimeout(() => {
      navigate("/checkout/success", { 
        state: { 
          planId, 
          amount: finalAmount,
          originalAmount: amount,
          discount: appliedDiscount 
        } 
      });
    }, 2000);
  };

  const applyDiscountCode = async () => {
    if (!discountCode.trim()) {
      toast.error("Please enter a discount code");
      return;
    }

    try {
      const validation = await revenueValidate(discountCode);
      
      if (validation.valid) {
        // Apply discount to the popular plan
        const popularPlan = plans.find(p => p.popular);
        const amount = isAnnual ? popularPlan.price.annual : popularPlan.price.monthly;
        
        const discount = await revenueApply(discountCode, amount);
        setAppliedDiscount(discount);
        toast.success(`Discount applied! Save ${discount.savings_percentage}%`);
      } else {
        toast.error(validation.message || "Invalid discount code");
      }
    } catch (error) {
      toast.error("Failed to apply discount code");
    }
  };

  const getPrice = (plan) => {
    if (appliedDiscount && plan.popular) {
      return isAnnual ? appliedDiscount.final_amount : Math.round(appliedDiscount.final_amount / 10);
    }
    return isAnnual ? plan.price.annual : plan.price.monthly;
  };

  const getOriginalPrice = (plan) => {
    return isAnnual ? plan.price.annual : plan.price.monthly;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">
            <Star className="h-4 w-4 mr-1" />
            Trusted by 50,000+ traders
          </Badge>
          
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Simple, Transparent Pricing
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Choose the perfect plan for your trading needs. Upgrade or downgrade at any time.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
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

          {/* Discount Code Input */}
          <div className="flex flex-col sm:flex-row gap-2 justify-center max-w-md mx-auto mb-8">
            <input
              type="text"
              placeholder="Enter discount code"
              value={discountCode}
              onChange={(e) => setDiscountCode(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md flex-1"
            />
            <Button onClick={applyDiscountCode} variant="outline">
              Apply
            </Button>
          </div>

          {appliedDiscount && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto mb-8">
              <p className="text-green-800">
                🎉 Discount applied! Save {appliedDiscount.savings_percentage}% with code "{appliedDiscount.code}"
              </p>
            </div>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
          {plans.map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative ${plan.popular ? 'ring-2 ring-blue-500 shadow-lg' : ''}`}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-600">
                  Most Popular
                </Badge>
              )}
              
              <CardHeader className="text-center">
                <div className={`w-12 h-12 mx-auto mb-4 rounded-lg flex items-center justify-center ${
                  plan.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                  plan.color === 'purple' ? 'bg-purple-100 text-purple-600' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {plan.icon}
                </div>
                
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription className="text-base">{plan.description}</CardDescription>
                
                <div className="mt-4">
                  <div className="flex items-baseline justify-center">
                    <span className="text-4xl font-bold">
                      ${getPrice(plan)}
                    </span>
                    {plan.price.monthly > 0 && (
                      <span className="text-gray-500 ml-1">
                        /{isAnnual ? 'year' : 'month'}
                      </span>
                    )}
                  </div>
                  
                  {appliedDiscount && plan.popular && getOriginalPrice(plan) !== getPrice(plan) && (
                    <div className="text-sm text-gray-500 line-through">
                      Was ${getOriginalPrice(plan)}/{isAnnual ? 'year' : 'month'}
                    </div>
                  )}
                  
                  {isAnnual && plan.price.monthly > 0 && (
                    <div className="text-sm text-green-600 mt-1">
                      Save ${(plan.price.monthly * 12) - plan.price.annual} per year
                    </div>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <Button
                  onClick={() => handlePlanSelect(plan.id)}
                  className="w-full"
                  variant={plan.popular ? "default" : "outline"}
                  disabled={isLoading}
                >
                  {plan.id === "free" ? "Current Plan" : "Get Started"}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Features included:</h4>
                  <ul className="space-y-2">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm">
                        <Check className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  
                  {plan.limitations.length > 0 && (
                    <>
                      <h4 className="font-semibold text-gray-900 mt-4">Limitations:</h4>
                      <ul className="space-y-2">
                        {plan.limitations.map((limitation, index) => (
                          <li key={index} className="flex items-center text-sm text-gray-500">
                            <X className="h-4 w-4 text-gray-400 mr-3 flex-shrink-0" />
                            {limitation}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Can I change plans at any time?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, 
                  and we'll prorate any differences.
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Is there a free trial?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Our Free plan gives you access to basic features forever. For premium features, 
                  we offer a 14-day free trial on all paid plans.
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">What payment methods do you accept?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  We accept all major credit cards, PayPal, and bank transfers. All payments are 
                  processed securely through our payment partners.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Still have questions?
          </h2>
          <p className="text-gray-600 mb-6">
            Our team is here to help you choose the right plan for your needs.
          </p>
          <Button asChild variant="outline" size="lg">
            <Link to="/contact">
              <CreditCard className="h-5 w-5 mr-2" />
              Contact Sales
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Pricing;