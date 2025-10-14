import React, { useState, useEffect } from "react";
import { trackEvent, trackPageView } from "../lib/analytics";
import SEO from "../components/SEO";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../components/ui/accordion";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
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
  Users,
  BarChart3,
  Bell,
  Shield,
  Mail,
  TrendingUp
} from "lucide-react";
import { useAuth } from "../context/SecureAuthContext";
import PayPalCheckout from "../components/PayPalCheckout";
import { createPayPalOrder, api } from "../api/client";
import { setPromoCookie, normalizePromoCode } from "../lib/promos";
import { normalizeReferralCode, setReferralCookie } from "../lib/referral";

const PricingPro = () => {
  const [isAnnual, setIsAnnual] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [checkoutPlan, setCheckoutPlan] = useState(null);
  const [plans, setPlans] = useState({});
  const [currentPlan, setCurrentPlan] = useState('free');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [referralCode, setReferralCode] = useState("");

  useEffect(() => {
    fetchPlans();
    try { trackPageView('/pricing'); } catch {}
  }, []);

  useEffect(() => {
    try {
      const state = location.state || {};
      let ref = "";
      if (state.discount_code && typeof state.discount_code === 'string') {
        ref = normalizeReferralCode(state.discount_code.replace(/^REF_/, ''));
      }
      if (!ref) {
        const params = new URLSearchParams(location.search || "");
        const qRef = params.get('ref');
        if (qRef && /^[A-Za-z0-9_-]{5,32}$/.test(qRef)) {
          ref = normalizeReferralCode(qRef);
        }
      }
      if (ref) {
        try { setReferralCookie(ref); } catch {}
        setReferralCode(ref);
      }
      // Capture generic promo code via ?code=
      try {
        const params = new URLSearchParams(location.search || "");
        const p = params.get('code');
        const norm = normalizePromoCode(p || '');
        if (norm) setPromoCookie(norm);
      } catch {}
    } catch {}
  }, [location.state, location.search]);

  const fetchPlans = async () => {
    try {
      const { data } = await api.get('/billing/plans-meta/');
      if (data?.success && data?.data) {
        // Expect data.data.plans shape; fallback to defaults if missing
        const normalized = data.data.plans && Object.keys(data.data.plans).length > 0 ? data.data.plans : getDefaultPlans();
        setPlans(normalized);
        setCurrentPlan((data.data.current_plan || 'free').toLowerCase());
      } else {
        setPlans(getDefaultPlans());
        setCurrentPlan('free');
      }
    } catch (error) {
      console.error('Failed to load plans-meta:', error);
      setPlans(getDefaultPlans());
      setCurrentPlan('free');
    }
  };

  const getDefaultPlans = () => ({
    free: {
      name: 'Free Plan',
      price: 0,
      price_yearly: 0,
      popular: false,
      limits: {
        api_calls: 30,
        screeners: 1,
        alerts: 0,
        watchlists: 1,
        portfolios: 1,
      },
      features: [
        'Stock data access',
        '30 API calls per month',
        'Basic stock screener',
        '1 screener',
        '1 portfolio'
      ]
    },
    bronze: {
      name: 'Bronze Plan', 
      price: 24.99,
      price_yearly: 254.99,
      popular: false,
      limits: {
        api_calls: 1500,
        screeners: 10,
        alerts: 50,
        watchlists: 2, 
        portfolios: 0,
      },
      features: [
        'Professional stock data access',
        '1,500 API calls per month',
        '10 Screeners',
        '100 Email Alerts per month',
        '2 Watchlists',
        'Real-time market information',
        'Basic stock screener',
        'Email alerts & notifications',
        'Portfolio tracking',
        'High Quality News and Sentiment Analysis',
        'Email support',
        'Advanced screener filters',
        'Custom watchlists',
        'Priority support'
      ]
    },
    silver: {
      name: 'Silver Plan',
      price: 49.99,
      price_yearly: 509.99,
      popular: true,
      limits: {
        api_calls: 5000,
        screeners: 20,
        alerts: 100,
        watchlists: 10,
        portfolios: 1,
      },
      features: [
        'All Bronze features',
        '5,000 API calls per month',
        '20 Screeners',
        '500 Alerts per month',
        '5 Watchlists',
        'Portfolio Analytics',
        'Advanced Screener Tools (JSON input/output)',
        'Advanced Watchlist Tools (JSON input/output)',
        'Historical data access',
        'Custom Portfolios',
        'Data Export (CSV, JSON)',
        'Priority support'
      ]
    },
    gold: {
      name: 'Gold Plan',
      price: 79.99,
      price_yearly: 814.99,
      popular: false,
      limits: {
        api_calls: -1,
        screeners: -1,
        alerts: -1,
        watchlists: -1,
        portfolios: -1,
      },
      features: [
        'Everything in Silver',
        'Unlimited API calls',
        'Unlimited everything',
        'API Key Access',
        'Developer Tools',
        'White-label Solutions',
        'Custom Reports',
        'Real-time market data',
        'Professional analytics',
        'Advanced export options',
        'Premium support'
      ]
    }
  });

  const getPlanIcon = (planKey) => {
    switch (planKey) {
      case 'free': return <Zap className="h-6 w-6" />;
      case 'bronze': return <Award className="h-6 w-6" />;
      case 'silver': return <Shield className="h-6 w-6" />;
      case 'gold': return <Crown className="h-6 w-6" />;
      default: return <Zap className="h-6 w-6" />;
    }
  };

  const getPlanColor = (planKey) => {
    switch (planKey) {
      case 'free': return 'text-gray-600 border-gray-200';
      case 'bronze': return 'text-orange-600 border-orange-200 bg-orange-50';
      case 'silver': return 'text-blue-600 border-blue-200 bg-blue-50';
      case 'gold': return 'text-yellow-600 border-yellow-200 bg-yellow-50';
      default: return 'text-gray-600 border-gray-200';
    }
  };

  const formatLimit = (limit) => {
    if (limit === -1) return 'Unlimited';
    return limit.toLocaleString();
  };

  // 15% annual discount, rounded to nearest price ending with 9.99
  const roundToNearest9_99 = (value) => {
    if (!value || value <= 0) return 0;
    const base = Math.floor(value / 10) * 10 + 9.99;
    const higher = base + 10;
    return Number((Math.abs(value - base) <= Math.abs(higher - value) ? base : higher).toFixed(2));
  };
  const computeAnnual = (monthly) => roundToNearest9_99(monthly * 12 * 0.85);
  const getAnnualSavings = (monthly) => {
    if (monthly === 0) return { amount: 0, percentage: 0 };
    const yearly = computeAnnual(monthly);
    const monthlyCost = monthly * 12;
    const savings = monthlyCost - yearly;
    const percentage = Math.round((savings / monthlyCost) * 100);
    return { amount: savings, percentage, yearly };
  };

  const handleSubscribe = async (planKey) => {
    if (!isAuthenticated) {
      navigate('/auth/sign-in');
      return;
    }
    try { trackEvent('begin_checkout', { items: [{ item_id: planKey, item_name: plans?.[planKey]?.name }], checkout_option: isAnnual ? 'annual' : 'monthly' }); } catch {}
    navigate('/checkout', { state: { plan: planKey, cycle: isAnnual ? 'annual' : 'monthly', discount_code: referralCode || undefined } });
  };

  const ctaLabel = (process.env.REACT_APP_CTA_LABEL || 'Try Free').trim();

  return (
      <div className="container mx-auto px-4 py-16">
      <SEO
        title="Pricing | Stock Filter & Market Scan Plans"
        description="Plans for stock filter and market scan workflows: real-time alerts, watchlists, portfolios, insider metrics, and in-depth stock info."
        url="https://tradescanpro.com/pricing"
        jsonLdUrls={["/structured/pricing-products.jsonld", "/structured/pricing-faq.jsonld"]}
      />
      {/* Header */}
      <div className="text-center mb-16">
        <Badge variant="secondary" className="mb-4">
          <Star className="h-4 w-4 mr-1" />
          Track 7,000+ NYSE & NASDAQ stocks with professional tools
        </Badge>
        
        <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">
          Choose Your Plan
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Professional stock scanning tools with real-time alerts and market intelligence
        </p>
        {/* Referral / Trial Messaging */}
        <div className="max-w-3xl mx-auto grid gap-3">
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-900 rounded-lg p-3 text-sm">
            7‑day trial for $1 on paid plans. Cancel anytime before renewal. Includes insider trading and fair value tools.
          </div>
          <div className="bg-blue-50 border border-blue-200 text-blue-900 rounded-lg p-3 text-sm">
            Have a referral? First month 50% off with your code at checkout.
          </div>
          {referralCode && (
            <div className="bg-green-50 border border-green-200 text-green-900 rounded-lg p-3 text-sm">
              Referral applied: <span className="font-semibold">{referralCode}</span> • 50% off first month
            </div>
          )}
        </div>
        
        {/* Billing Toggle */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <Label htmlFor="billing-toggle" className={isAnnual ? "text-gray-600" : "text-gray-900 font-medium"}>
            Monthly
          </Label>
          <Switch
            id="billing-toggle"
            checked={isAnnual}
            onCheckedChange={setIsAnnual}
          />
          <Label htmlFor="billing-toggle" className={isAnnual ? "text-gray-900 font-medium" : "text-gray-600"}>
            Annual
          </Label>
          <Badge variant="secondary" className="bg-green-100 text-green-800 ml-2">
            Save 15%
          </Badge>
        </div>
      </div>

      {/* Sticky Desktop CTA on Pricing */}
      <div className="hidden md:block">
        <div className="fixed bottom-6 right-6 z-40">
          <Button asChild size="lg" className="shadow-lg bg-blue-600 hover:bg-blue-700">
            <Link to="/auth/sign-up">{ctaLabel}</Link>
          </Button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        {Object.entries(plans).map(([planKey, plan]) => {
          const savings = getAnnualSavings(plan.price);
          
          return (
            <Card key={planKey} className={`relative ${plan.popular ? 'ring-2 ring-blue-500 shadow-lg' : ''} ${getPlanColor(planKey)}`}>
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white">
                  Most Popular
                </Badge>
              )}
              
              <CardHeader className="text-center pb-4">
                <div className="flex justify-center mb-4">
                  {getPlanIcon(planKey)}
                </div>
                <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                <div className="mt-4">
                  <div className="text-4xl font-bold text-gray-900">
                    ${(() => {
                      if (plan.price === 0) return 0;
                      if (referralCode && !isAnnual) {
                        return (plan.price * 0.5).toFixed(2);
                      }
                      return isAnnual ? savings.yearly : plan.price;
                    })()}
                    {plan.price > 0 && (
                      <span className="text-lg font-normal text-gray-600">
                        /{isAnnual ? 'year' : 'month'}
                      </span>
                    )}
                  </div>
                  {isAnnual && plan.price > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-600">{(savings.yearly / 12).toFixed(2)}/month billed annually</p>
                      <Badge variant="secondary" className="bg-green-100 text-green-800 mt-1">
                        Save ${savings.amount.toFixed(2)} ({savings.percentage}%)
                      </Badge>
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="pt-0">
                {/* Limits Summary */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">API Calls:</span>
                      <span className="font-medium ml-1">{formatLimit(plan.limits.api_calls)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Screeners:</span>
                      <span className="font-medium ml-1">{formatLimit(plan.limits.screeners)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Alerts:</span>
                      <span className="font-medium ml-1">{formatLimit(plan.limits.alerts)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Watchlists:</span>
                      <span className="font-medium ml-1">{formatLimit(plan.limits.watchlists)}</span>
                    </div>
                  </div>
                </div>

                {/* Features List */}
                <ul className="space-y-3 mb-8">
                  {plan.features.slice(0, 6).map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </li>
                  ))}
                  {plan.features.length > 6 && (
                    <li className="text-sm text-gray-500">
                      + {plan.features.length - 6} more features
                    </li>
                  )}
                </ul>

                {/* CTA Button */}
                <div className="space-y-3">
                  <Button
                    className={`w-full ${
                      plan.popular
                        ? 'bg-blue-600 hover:bg-blue-700'
                        : currentPlan === planKey
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gray-900 hover:bg-gray-800'
                    }`}
                    onClick={() => handleSubscribe(planKey)}
                    disabled={isLoading || currentPlan === planKey || planKey === 'free'}
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Processing...</span>
                      </div>
                    ) : currentPlan === planKey ? (
                      'Current Plan'
                    ) : planKey === 'free' ? (
                      'Get Started Free'
                    ) : (
                      planKey === 'free' ? ctaLabel : `Upgrade to ${plan.name}`
                    )}
                  </Button>
                  {/* Trial / Referral note under CTAs */}
                  {planKey !== 'free' && (
                    <p className="text-xs text-gray-500 text-center">
                      $1 for 7 days • 50% off 1st month with referral code
                    </p>
                  )}
                  
                  {planKey === 'free' && !isAuthenticated && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => navigate('/auth/sign-up')}
                    >
                      Create Free Account
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Checkout moved to /checkout */}

      {/* Which plan is right for me? */}
      <div className="max-w-4xl mx-auto mb-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">Which plan is right for me?</h2>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          <div className="bg-white border rounded-lg p-4">
            <p className="font-semibold text-gray-900 mb-1">Free</p>
            <p className="text-gray-600">Trying the platform; basic lookup and 1 portfolio.</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="font-semibold text-gray-900 mb-1">Bronze</p>
            <p className="text-gray-600">Casual trader; 10 screeners, 2 watchlists, 50 alerts/month.</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="font-semibold text-gray-900 mb-1">Silver</p>
            <p className="text-gray-600">Active trader; 20 screeners, 10 watchlists, 100 alerts, 1 portfolio.</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="font-semibold text-gray-900 mb-1">Gold</p>
            <p className="text-gray-600">Power user/team; unlimited limits and premium support.</p>
          </div>
        </div>
      </div>

      {/* API Call Pricing Explanation */}
      <div className="bg-gray-50 rounded-lg p-8 mb-16">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Understanding API Call Usage
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="text-center">
            <BarChart3 className="h-8 w-8 mx-auto mb-3 text-blue-600" />
            <h4 className="font-semibold mb-2">Stock List Views</h4>
            <p className="text-sm text-gray-600">Listing all stocks = 5 API calls</p>
          </div>
          <div className="text-center">
            <TrendingUp className="h-8 w-8 mx-auto mb-3 text-green-600" />
            <h4 className="font-semibold mb-2">Individual Stock Data</h4>
            <p className="text-sm text-gray-600">One stock details = 1 API call</p>
          </div>
          <div className="text-center">
            <Shield className="h-8 w-8 mx-auto mb-3 text-orange-600" />
            <h4 className="font-semibold mb-2">Screener Runs</h4>
            <p className="text-sm text-gray-600">Running a screener = 2 API calls</p>
          </div>
          <div className="text-center">
            <Bell className="h-8 w-8 mx-auto mb-3 text-red-600" />
            <h4 className="font-semibold mb-2">Alert Creation</h4>
            <p className="text-sm text-gray-600">Adding an alert = 2 API calls</p>
          </div>
          <div className="text-center">
            <Users className="h-8 w-8 mx-auto mb-3 text-purple-600" />
            <h4 className="font-semibold mb-2">Market Data</h4>
            <p className="text-sm text-gray-600">Loading market page = 2 API calls</p>
          </div>
          <div className="text-center">
            <Star className="h-8 w-8 mx-auto mb-3 text-yellow-600" />
            <h4 className="font-semibold mb-2">Watchlist Creation</h4>
            <p className="text-sm text-gray-600">Making a watchlist = 2 API calls</p>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto">
        <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
          Frequently Asked Questions
        </h3>
        <Accordion type="single" collapsible className="bg-white rounded-lg border">
          <AccordionItem value="item-1">
            <AccordionTrigger>What happens if I exceed my API limit?</AccordionTrigger>
            <AccordionContent>
              Once you reach your monthly API limit, you'll need to upgrade to continue using the service. We'll notify you when you're approaching your limit.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-2">
            <AccordionTrigger>Can I change plans anytime?</AccordionTrigger>
            <AccordionContent>
              Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and billing is prorated.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-3">
            <AccordionTrigger>What's included in the free plan?</AccordionTrigger>
            <AccordionContent>
              The free plan includes stock data access, 30 API calls per month, basic stock screener (30 calls, 1 screener, 1 portfolio).
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-4">
            <AccordionTrigger>How much do I save with annual billing?</AccordionTrigger>
            <AccordionContent>
              Annual plans save you 15% compared to monthly billing. For example, Bronze saves $44.89/year, Silver saves $89.89/year, and Gold saves $144.89/year.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-5">
            <AccordionTrigger>Do you offer refunds?</AccordionTrigger>
            <AccordionContent>
              Refunds are not guaranteed; trials are available and you may cancel anytime before renewal. For questions, contact {process.env.REACT_APP_SUPPORT_EMAIL || 'noreply.retailtradescanner@gmail.com'}.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>

      {/* Contact Support */}
      <div className="text-center mt-16">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Need help choosing a plan?
        </h3>
        <p className="text-gray-600 mb-6">
          Contact our team for personalized recommendations.
        </p>
        <Button asChild variant="outline" size="lg">
          <Link to="/contact">
            <Mail className="h-5 w-5 mr-2" />
            Contact Support
          </Link>
        </Button>
      </div>
    </div>
  );
};

export default PricingPro;