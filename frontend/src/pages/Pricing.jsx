import React, { useState, useEffect } from "react";
import SEO from "../components/SEO";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../components/ui/collapsible";
import { toast } from "sonner";
import { 
  Check, 
  X, 
  Zap, 
  Crown, 
  Award,
  Star,
  ArrowRight,
  CreditCard,
  ChevronDown,
  Users,
  BarChart3,
  Bell,
  Shield,
  Mail
} from "lucide-react";
import { useAuth } from "../context/SecureAuthContext";
import { normalizeReferralCode, setReferralCookie } from "../lib/referral";

const Pricing = () => {
  const [isAnnual, setIsAnnual] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [discountCode, setDiscountCode] = useState("");
  const [appliedDiscount, setAppliedDiscount] = useState(null);
  const [referralCode, setReferralCode] = useState("");
  const [openComparison, setOpenComparison] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  useEffect(() => {
    // Auto-apply discount_code from navigation state (e.g., referral from plan selection)
    try {
      const state = location.state || {};
      if (state.discount_code && typeof state.discount_code === 'string') {
        setDiscountCode(state.discount_code);
        setAppliedDiscount({ code: state.discount_code, description: 'Referral discount (first month 50%)', savings_percentage: 50, final_amount: null });
        try { setReferralCookie(state.discount_code); } catch {}
      }
    } catch {}
  }, [location.state]);

  useEffect(() => {
    // Read ?ref=abc12 and show referral banner; auto-fill discount field with REF_*
    try {
      const params = new URLSearchParams(location.search || "");
      const qRef = params.get('ref');
      if (qRef && /^[A-Za-z0-9_-]{5,32}$/.test(qRef)) {
        const code = normalizeReferralCode(qRef);
        setReferralCode(code);
        setDiscountCode(code);
        setAppliedDiscount({ code, description: 'Referral discount (first month 50%)', savings_percentage: 50, final_amount: null });
        try { setReferralCookie(code); } catch {}
      }
    } catch {}
  }, [location.search]);

  const plans = [
    {
      id: "bronze",
      name: "Bronze",
      icon: <Award className="h-6 w-6" />,
      description: "Enhanced features for active traders",
      price: { monthly: 24.99, annual: null },
      features: [
        "150 API calls per day, 1500/month",
        "Full stock scanner & lookup",
        "Email alerts & notifications",
        "Real-time alerts (50 alerts/mo)",
        "2 Watchlists",
        "No portfolios"
      ],
      limitations: [],
      popular: true,
      color: "orange",
      cta: "Try for free"
    },
    {
      id: "silver",
      name: "Silver",
      icon: <Crown className="h-6 w-6" />,
      description: "Professional tools for serious traders",
      price: { monthly: 49.99, annual: null },
      features: [
        "500 API calls per day, 5000/month",
        "Advanced filtering & screening",
        "Custom watchlists (10)",
        "Real-time alerts (100 alerts/mo)",
        "Portfolio tracking (1 portfolio)",
        "Priority email support"
      ],
      limitations: [],
      popular: false,
      color: "blue",
      cta: "Try for free"
    },
    {
      id: "gold",
      name: "Gold",
      icon: <Star className="h-6 w-6" />,
      description: "Ultimate trading experience",
      price: { monthly: 89.99, annual: null },
      features: [
        "Unlimited API calls",
        "All premium features",
        "Real-time alerts",
        "Full REST API access",
        "Priority email support"
      ],
      limitations: [],
      popular: false,
      color: "yellow",
      cta: "Try for free"
    },
    // Free plan removed per policy
  ];

  // Annual pricing: 15% off, rounded to nearest value ending in 9.99
  const roundToNearest9_99 = (value) => {
    if (!value || value <= 0) return 0;
    const base = Math.floor(value / 10) * 10 + 9.99;
    const higher = base + 10;
    return Number((Math.abs(value - base) <= Math.abs(higher - value) ? base : higher).toFixed(2));
  };

  const computeAnnual = (monthly) => roundToNearest9_99(monthly * 12 * 0.85);

  const handlePlanSelect = async (planId) => {
    if (!isAuthenticated) {
      navigate("/auth/sign-up", { 
        state: { selectedPlan: planId, discountCode: discountCode } 
      });
      return;
    }

    // Free plan removed

    setIsLoading(true);
    
    try {
      const plan = plans.find(p => p.id === planId);
      const amount = isAnnual ? plan.price.annual : plan.price.monthly;
      
      // Create PayPal checkout without $1 trial
      await createPayPalOrder(planId);
    } catch (error) {
      toast.error("Failed to create checkout session");
    } finally {
      setIsLoading(false);
    }
  };

  const createPayPalOrder = async (planId) => {
    toast.success("Redirecting to PayPal...");
    
    // Simulate redirect to PayPal
    setTimeout(() => {
      navigate("/checkout/success", { 
        state: { 
          planId, 
          amount: finalAmount,
          originalAmount: plans.find(p => p.id === planId).price.monthly
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
      toast.error("No trial codes. Trial is free until next 1st.");
    } catch (error) {
      toast.error("Failed to apply discount code");
    }
  };

  const features = [
    {
      category: "Stock Analysis",
      icon: <BarChart3 className="h-5 w-5" />,
      items: [
        { name: "Monthly stock queries", free: "15", bronze: "100/day, 1500/month", silver: "500/day, 5000/month", gold: "Unlimited" },
        { name: "Stock symbol lookup", free: true, bronze: true, silver: true, gold: true },
        { name: "Basic price filtering", free: true, bronze: true, silver: true, gold: true },
        { name: "Advanced screening", free: false, bronze: true, silver: true, gold: true },
        { name: "Real-time data", free: false, bronze: true, silver: true, gold: true }
      ]
    },
    {
      category: "Alerts & Notifications",
      icon: <Bell className="h-5 w-5" />,
      items: [
        { name: "Email alerts", free: false, bronze: true, silver: true, gold: true },
        { name: "Real-time alerts", free: false, bronze: "50 alerts", silver: "100 alerts", gold: true },
        { name: "Custom alert conditions", free: false, bronze: "Basic", silver: "Advanced", gold: "Unlimited" }
      ]
    },
    {
      category: "Portfolio & Tracking",
      icon: <Users className="h-5 w-5" />,
      items: [
        { name: "Portfolio management", free: false, bronze: "No portfolios", silver: "1 portfolio", gold: "Professional" },
        { name: "Watchlists", free: false, bronze: "2", silver: "10", gold: "Unlimited" },
        { name: "Performance analytics", free: false, bronze: false, silver: true, gold: true }
      ]
    },
    {
      category: "Support & API",
      icon: <Mail className="h-5 w-5" />,
      items: [
        { name: "Email support", free: false, bronze: true, silver: true, gold: true },
        { name: "Priority support", free: false, bronze: false, silver: true, gold: true },
        { name: "API access", free: false, bronze: false, silver: "Limited", gold: "Full" }
      ]
    }
  ];

  const getPrice = (plan) => {
    if (appliedDiscount && plan.id !== "free") {
      return 1.00;
    }
    return isAnnual ? computeAnnual(plan.price.monthly) : plan.price.monthly;
  };

  const getColorClasses = (color) => {
    switch (color) {
      case 'orange': return 'bg-orange-100 text-orange-600 border-orange-500';
      case 'blue': return 'bg-blue-100 text-blue-600 border-blue-500';
      case 'yellow': return 'bg-yellow-100 text-yellow-600 border-yellow-500';
      default: return 'bg-gray-100 text-gray-600 border-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 py-12">
      <SEO
        title="Pricing (Legacy) | Trade Scan Pro"
        description="Legacy pricing page for Trade Scan Pro plans."
        url="https://tradescanpro.com/pricing-old"
        jsonLdUrls={["/structured/pricing-products.jsonld", "/structured/pricing-faq.jsonld"]}
        robots="noindex,follow"
      />
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">
            <Star className="h-4 w-4 mr-1" />
            Trusted by thousands of traders worldwide
          </Badge>
          
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Simple, Transparent Pricing
          </h1>
          
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Try for free until the next 1st of the month. Cancel anytime.
            </p>

          {/* Social proof logo bar + trust markers */}
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500 mb-6">
            <span>As seen on</span>
            <span className="font-medium">TradingView</span>
            <span className="font-medium">Finviz</span>
            <span className="font-medium">Product Hunt</span>
            <a href="/endpoint-status" className="underline hover:no-underline">Status & Uptime</a>
            <span className="font-medium">Bank‑Level Security</span>
          </div>

          {/* Trust Banner with guarantee */}
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg p-6 max-w-2xl mx-auto mb-8">
            <div className="flex items-center justify-center mb-3">
              <Zap className="h-6 w-6 mr-2" />
              <span className="text-lg font-bold">Trial</span>
            </div>
            <p className="text-xl mb-4">Try for free until the next 1st of the month</p>
            <p className="text-sm opacity-90">Then continue at regular price or cancel anytime. Money‑back guarantee.</p>
          </div>

          {/* Referral Notice */}
          {referralCode && (
            <div className="bg-blue-50 border border-blue-200 text-blue-900 rounded-lg p-4 max-w-2xl mx-auto mb-8">
              Referral applied: <span className="font-semibold">{referralCode}</span> • 50% off first month
            </div>
          )}

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
              <Badge variant="secondary" className="ml-2">Save 15%</Badge>
            </Label>
          </div>

          {/* Discount codes disabled for trial policy */}

          {appliedDiscount && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto mb-8">
              <p className="text-green-800">
                🎉 {appliedDiscount.description} - Save {appliedDiscount.savings_percentage}%!
              </p>
            </div>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-4 gap-6 max-w-7xl mx-auto mb-16">
          {plans.map((plan) => (
            <Card 
              key={plan.id} 
              className={`relative hover:shadow-xl transition-all duration-300 ${
                plan.popular ? 'ring-2 ring-orange-500 shadow-lg scale-105' : ''
              }`}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-orange-600">
                  Most Popular
                </Badge>
              )}
              
              <CardHeader className="text-center">
                <div className={`w-16 h-16 mx-auto mb-4 rounded-xl flex items-center justify-center ${getColorClasses(plan.color)}`}>
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
                  
                  {appliedDiscount && plan.id !== "free" && (
                    <div className="text-sm text-gray-500 line-through mt-1">
                      Was ${isAnnual ? computeAnnual(plan.price.monthly) : plan.price.monthly}/{isAnnual ? 'year' : 'month'}
                    </div>
                  )}
                  
                  {isAnnual && plan.price.monthly > 0 && !appliedDiscount && (
                    <div className="text-sm text-green-600 mt-1">
                      Save ${((plan.price.monthly * 12) - computeAnnual(plan.price.monthly)).toFixed(2)} per year
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
                  {plan.cta}
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

        {/* Feature Comparison Table */}
        <Collapsible open={openComparison} onOpenChange={setOpenComparison} className="mb-16">
          <div className="text-center mb-8">
            <CollapsibleTrigger asChild>
              <Button variant="outline" size="lg">
                <BarChart3 className="h-5 w-5 mr-2" />
                Compare All Features
                <ChevronDown className={`h-5 w-5 ml-2 transition-transform ${openComparison ? 'rotate-180' : ''}`} />
              </Button>
            </CollapsibleTrigger>
          </div>
          
          <CollapsibleContent>
            <Card>
              <CardHeader className="text-center">
                <CardTitle>Complete Feature Comparison</CardTitle>
                <CardDescription>See exactly what's included in each plan</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-4 font-medium">Features</th>
                        <th className="text-center p-4 font-medium">Free</th>
                        <th className="text-center p-4 font-medium">Bronze</th>
                        <th className="text-center p-4 font-medium">Silver</th>
                        <th className="text-center p-4 font-medium">Gold</th>
                      </tr>
                    </thead>
                    <tbody>
                      {features.map((category) => (
                        <React.Fragment key={category.category}>
                          <tr className="bg-gray-50">
                            <td colSpan="5" className="p-4 font-semibold text-gray-900 flex items-center">
                              {category.icon}
                              <span className="ml-2">{category.category}</span>
                            </td>
                          </tr>
                          {category.items.map((item, index) => (
                            <tr key={index} className="border-b">
                              <td className="p-4">{item.name}</td>
                              <td className="p-4 text-center">
                                {typeof item.free === 'boolean' ? 
                                  (item.free ? <Check className="h-4 w-4 text-green-500 mx-auto" /> : <X className="h-4 w-4 text-gray-400 mx-auto" />) :
                                  item.free
                                }
                              </td>
                              <td className="p-4 text-center">
                                {typeof item.bronze === 'boolean' ? 
                                  (item.bronze ? <Check className="h-4 w-4 text-green-500 mx-auto" /> : <X className="h-4 w-4 text-gray-400 mx-auto" />) :
                                  item.bronze
                                }
                              </td>
                              <td className="p-4 text-center">
                                {typeof item.silver === 'boolean' ? 
                                  (item.silver ? <Check className="h-4 w-4 text-green-500 mx-auto" /> : <X className="h-4 w-4 text-gray-400 mx-auto" />) :
                                  item.silver
                                }
                              </td>
                              <td className="p-4 text-center">
                                {typeof item.gold === 'boolean' ? 
                                  (item.gold ? <Check className="h-4 w-4 text-green-500 mx-auto" /> : <X className="h-4 w-4 text-gray-400 mx-auto" />) :
                                  item.gold
                                }
                              </td>
                            </tr>
                          ))}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </CollapsibleContent>
        </Collapsible>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-4">
            <Card>
              <CardHeader>
              <CardTitle className="text-lg">How does the free trial work?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Your trial lasts until the next 1st of the month. No $1 trial codes.
                  You'll be charged the regular price on the 1st unless you cancel before then.
                </p>
              </CardContent>
            </Card>
            
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
                <CardTitle className="text-lg">What payment methods do you accept?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  We accept all major credit cards and PayPal. All payments are processed securely 
                  with industry-standard encryption.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
              <CardTitle className="text-lg">Is there a free plan available?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  No. We no longer offer a free plan. Instead, trials are free until the next 1st of the month.
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