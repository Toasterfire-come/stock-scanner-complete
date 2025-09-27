import React, { useState, useEffect, Suspense, lazy } from "react";
import SEO from "../components/SEO";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../components/ui/collapsible";
import { 
  TrendingUp, 
  Search, 
  Bell, 
  Shield, 
  BarChart3, 
  Zap,
  ArrowRight,
  Star,
  Users,
  CheckCircle,
  ChevronDown,
  Play,
  DollarSign,
  Target,
  Clock,
  Award,
  Mail
} from "lucide-react";
import { getMarketStatsSafe } from "../api/client";
import MarketStatus from "../components/MarketStatus";
import { toast } from "sonner";
const QuickMiniFAQ = lazy(() => import("../components/home/QuickMiniFAQ"));
const ScreenerDemo = lazy(() => import("../components/home/ScreenerDemo"));
const TestimonialsSection = lazy(() => import("../components/home/TestimonialsSection"));
const HomeFAQ = lazy(() => import("../components/home/HomeFAQ"));

function useExitIntent(callback, enabled = true) {
  useEffect(() => {
    if (!enabled) return;
    let triggered = false;
    const onMouseLeave = (e) => {
      if (triggered) return;
      if (e.clientY <= 0) {
        triggered = true;
        callback();
      }
    };
    document.addEventListener('mouseleave', onMouseLeave);
    return () => document.removeEventListener('mouseleave', onMouseLeave);
  }, [callback, enabled]);
}

const Home = () => {
  const [marketStats, setMarketStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  const [showExitIntent, setShowExitIntent] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const statsResponse = await getMarketStatsSafe();
        if (statsResponse.success && !statsResponse.fallback) {
          setMarketStats(statsResponse.data);
        }
        // If using fallback data, don't show stats
      } catch (error) {
        console.error("Failed to fetch market data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    // First-time onboarding tooltips (simple toasts)
    try {
      const seen = localStorage.getItem('onboarding-tooltips-v1') === '1';
      if (!seen) {
        setTimeout(() => {
          try { toast.info('Tip: Create your first screener', { description: 'Go to Screeners > New to find trade setups.' }); } catch {}
        }, 800);
        setTimeout(() => {
          try { toast.info('Tip: Add to watchlist', { description: 'Use the star/bookmark buttons across the app.' }); } catch {}
        }, 2000);
        localStorage.setItem('onboarding-tooltips-v1', '1');
      }
    } catch {}
  }, []);

  // Exit intent modal toggle
  useExitIntent(() => setShowExitIntent(true), true);

  const features = [
    {
      icon: <Search className="h-6 w-6" />,
      title: "Advanced Stock Screening",
      description: "Screen 10,500+ NYSE & NASDAQ stocks with 14 technical and fundamental criteria including real-time data analysis.",
      details: "Our proprietary screening engine processes millions of data points daily to help you find the perfect investment opportunities."
    },
    {
      icon: <Bell className="h-6 w-6" />,
      title: "Real-Time Alerts",
      description: "Never miss a trading opportunity with instant price and volume alerts.",
      details: "Set custom alerts for price movements, volume spikes, news events, and technical indicators. Get notified via email, SMS, or push notifications."
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Portfolio Analytics",
      description: "Track performance with institutional-grade portfolio management tools.",
      details: "Advanced risk metrics, performance attribution, sector allocation analysis, and detailed profit/loss tracking with tax reporting."
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "Market Intelligence",
      description: "AI-powered insights and sentiment analysis from news and social media.",
      details: "Our machine learning algorithms analyze thousands of news articles and social media posts to gauge market sentiment and predict price movements."
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Professional Day Trader",
      company: "Peak Capital Trading",
      content: "Trade Scan Pro has completely transformed my trading strategy. The screening tools are incredibly powerful and have helped me identify winning trades that I would have missed otherwise.",
      rating: 5,
      profit: "+342% ROI in 6 months"
    },
    {
      name: "Michael Rodriguez",
      role: "Portfolio Manager",
      company: "Evergreen Investments",
      content: "The real-time alerts have saved me from multiple significant losses. The platform's reliability and accuracy are unmatched in the industry.",
      rating: 5,
      profit: "Prevented $50K+ in losses"
    },
    {
      name: "Jennifer Park",
      role: "Investment Advisor",
      company: "Wealth Strategies LLC",
      content: "My clients love the detailed reports and easy-to-understand visualizations. It's become an essential tool for our investment process.",
      rating: 5,
      profit: "Managing $2.3M in assets"
    }
  ];

  const faqs = [
    {
      question: "How accurate is your market data?",
      answer: "Our data is sourced directly from major exchanges and updated in real-time. We maintain 99.9% uptime and ensure data accuracy through multiple validation layers."
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Yes, you can cancel your subscription at any time. There are no long-term contracts or cancellation fees. Your subscription will remain active until the end of your current billing period."
    },
    {
      question: "Do you offer API access?",
      answer: "Yes! Our Silver and Gold plans include full REST API access, allowing you to integrate our data into your own applications and trading systems."
    },
    {
      question: "What's the difference between plans?",
      answer: "Plans differ mainly in the number of API calls per month, available features, and support level. Free plan includes 30 calls/month, Bronze is great for casual traders, Silver for active traders, and Gold for professional traders and institutions."
    },
    {
      question: "How does the API call counting work?",
      answer: "Different operations consume different amounts of API calls: listing all stocks (5 calls), single stock data (1 call), running screeners (2 calls), creating alerts (2 calls), loading market data (2 calls), and making watchlists (2 calls)."
    }
  ];

  const stats = [
    { label: "Active Traders", value: "50,000+", icon: <Users className="h-5 w-5" /> },
    { label: "Stocks Tracked", value: "10,500+", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "Daily Alerts Sent", value: "1M+", icon: <Bell className="h-5 w-5" /> },
    { label: "API Calls/Month", value: "100M+", icon: <Zap className="h-5 w-5" /> }
  ];

  const pricingPlans = [
    {
      name: "Free",
      price: "$0",
      period: "/forever",
      description: "Perfect for getting started",
      features: [
        "30 API calls per month",
        "Basic stock data access",
        "1 Basic stock screener",
        "1 Portfolio",
        "Community support"
      ],
      popular: false,
      cta: "Get Started Free",
      isFree: true
    },
    {
      name: "Bronze",
      price: "$24.99",
      period: "/month",
      annualPrice: "$254.99",
      description: "Enhanced features for active traders",
      features: [
        "1500 API calls per month",
        "10 Screeners",
        "50 Alerts per month",
        "2 Watchlists",
        "No portfolios",
        "Professional stock data access",
        "Real-time market information",
        "High Quality News and Sentiment Analysis",
        "Email support"
      ],
      popular: true,
      cta: "Start Free Trial"
    },
    {
      name: "Silver", 
      price: "$49.99",
      period: "/month",
      annualPrice: "$509.99",
      description: "Professional tools for serious traders",
      features: [
        "5000 API calls per month",
        "20 Screeners",
        "100 Alerts per month",
        "10 Watchlists",
        "1 Portfolio",
        "Portfolio Analytics",
        "Advanced Screener Tools (JSON input/output)",
        "Advanced Watchlist Tools",
        "Historical data access",
        "Priority support"
      ],
      popular: false,
      cta: "Start Free Trial"
    },
    {
      name: "Gold",
      price: "$79.99", 
      period: "/month",
      annualPrice: "$814.99",
      description: "Ultimate trading experience",
      features: [
        "Unlimited Everything",
        "Professional stock data access",
        "Highest Limits",
        "Portfolio tracking (unlimited)",
        "All Screener and Watchlist Tools",
        "API Key Access",
        "Real-time market data",
        "Professional reporting"
      ],
      popular: false,
      cta: "Start Free Trial"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Trade Scan Pro | Professional Stock Market Scanner"
        description="Advanced stock screening, real-time alerts, portfolio analytics, and market intelligence for serious traders."
        url="https://tradescanpro.com/"
        jsonLdUrls={["/structured/website.jsonld", "/structured/software.jsonld", "/structured/organization.jsonld"]}
      />
      {/* Hero Section - Conversion Focused */}
      <section className="relative overflow-hidden py-12 sm:py-20 lg:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-5xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-base sm:text-lg px-4 py-2">
              <Award className="h-4 w-4 mr-2" />
              Trusted by 50,000+ Professional Traders
            </Badge>
            
            <h1 className="text-3xl sm:text-5xl lg:text-7xl font-bold text-gray-900 mb-6 sm:mb-8 leading-tight">
              Find NYSE & NASDAQ Winners in Minutes
              <span className="text-blue-600 block"> with Real‑Time Screeners</span>
            </h1>
            
            <p className="text-lg sm:text-xl lg:text-2xl text-gray-700 mb-8 sm:mb-12 max-w-4xl mx-auto leading-relaxed">
              Join thousands of successful traders using our advanced screening tools, 
              real-time alerts, and AI-powered market intelligence to maximize their returns.
            </p>
            
            {/* Market Status */}
            <div className="mb-6 sm:mb-8 flex justify-center">
              <MarketStatus showNotice={true} />
            </div>

            {/* Primary CTA + Inline Email Capture */}
            <div className="flex flex-col items-center gap-4 sm:gap-6 justify-center mb-8 sm:mb-12">
              <div className="flex flex-col sm:flex-row gap-3">
                <Button asChild size="lg" className="text-lg sm:text-xl px-8 sm:px-12 py-4 sm:py-6 h-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
                  <Link to="/auth/sign-up">
                    <Play className="h-5 w-5 sm:h-6 sm:w-6 mr-2 sm:mr-3" />
                    Try free — no card required
                    <ArrowRight className="h-5 w-5 sm:h-6 sm:w-6 ml-2 sm:ml-3" />
                  </Link>
                </Button>
              </div>
              <form
                className="w-full max-w-md flex gap-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  const email = (e.currentTarget.elements.namedItem('hero_email')?.value || '').toString();
                  if (!email) return;
                  // Navigate and prefill email
                  try { window.history.replaceState({}, '', window.location.pathname); } catch(e) {}
                  navigate('/auth/sign-up', { state: { emailPrefill: email } });
                }}
              >
                <input
                  type="email"
                  name="hero_email"
                  required
                  placeholder="Enter your email"
                  className="flex-1 px-4 py-3 rounded-md border border-gray-300"
                />
                <Button type="submit" className="px-5">Start</Button>
              </form>
              <div className="text-xs text-gray-500">Cancel anytime • 7‑day trial for $1 • No card needed for Free plan</div>
            </div>

            {/* Logos / Social Proof */}
            <div className="mt-4 text-xs sm:text-sm text-gray-500 flex flex-wrap justify-center gap-4">
              <span>As seen on</span>
              <span className="font-medium">TradingView</span>
              <span className="font-medium">Finviz</span>
              <span className="font-medium">Product Hunt</span>
              <span className="font-medium">Medium</span>
              <a href="/status" className="underline hover:no-underline">Status & Uptime</a>
            </div>

            {/* Quick FAQ near hero */}
            <Suspense fallback={null}>
              <QuickMiniFAQ />
            </Suspense>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-8 text-sm sm:text-lg text-gray-600">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-green-500 mr-2 sm:mr-3" />
                Email Support Only
              </div>
              <div className="flex items-center">
                <Shield className="h-4 w-4 sm:h-5 sm:w-5 text-blue-500 mr-2 sm:mr-3" />
                Bank-Level Security
              </div>
              <div className="flex items-center">
                <Clock className="h-4 w-4 sm:h-5 sm:w-5 text-purple-500 mr-2 sm:mr-3" />
                Cancel Anytime
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Sticky Mobile CTA */}
      <div className="fixed bottom-4 left-0 right-0 z-40 block sm:hidden">
        <div className="mx-4 rounded-xl shadow-lg bg-white border flex items-center justify-between px-4 py-3">
          <div className="text-sm text-gray-700">
            Try free — no card required
          </div>
          <Button asChild size="sm" className="ml-3 bg-blue-600 hover:bg-blue-700">
            <Link to="/auth/sign-up">Try Free</Link>
          </Button>
        </div>
      </div>
      {/* Sticky Desktop CTA */}
      <div className="hidden sm:block">
        <div className="fixed bottom-6 right-6 z-40">
          <Button asChild size="lg" className="shadow-lg bg-blue-600 hover:bg-blue-700">
            <Link to="/auth/sign-up">Try free — no card required</Link>
          </Button>
        </div>
      </div>
      {/* Testimonial Snippet */}
      <section className="py-6 sm:py-8 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-gray-50 border rounded-lg p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex-1">
                <p className="text-gray-900 text-base sm:text-lg font-medium mb-1">“{testimonials[0].content}”</p>
                <p className="text-sm text-gray-600">{testimonials[0].name} — {testimonials[0].role}</p>
              </div>
              <div className="text-sm text-green-700 font-semibold">{testimonials[0].profit}</div>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Results */}
      <section className="py-10 sm:py-14 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-6 sm:mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Sample Screener Results</h2>
            <p className="text-gray-600">Why these tickers matched today</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 max-w-6xl mx-auto">
            {[{t:'AAPL',r:'50DMA crossover + volume > 1.5× avg'}, {t:'MSFT',r:'RSI 60–70 with positive price action'}, {t:'NVDA',r:'Momentum continuation; MACD bullish'}].map((s, i) => (
              <div key={i} className="bg-white rounded-lg border p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-lg font-semibold text-gray-900">{s.t}</div>
                  <span className="text-xs text-gray-500">NYSE/NASDAQ</span>
                </div>
                <p className="text-sm text-gray-700">{s.r}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Screener Demo */}
      <Suspense fallback={null}>
        <ScreenerDemo />
      </Suspense>

      {/* Social Proof Stats */}
      {marketStats && marketStats.market_overview && (
        <section className="py-12 sm:py-16 bg-white border-y">
          <div className="container mx-auto px-4">
            <div className="text-center mb-8 sm:mb-12">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Live Market Performance</h2>
              <p className="text-gray-600">Real-time data from our trading platform</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8">
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold text-blue-600 mb-2">
                  {Number(marketStats?.market_overview?.total_stocks ?? 0).toLocaleString()}
                </div>
                <div className="text-sm sm:text-base text-gray-600">Stocks Analyzed Today</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold text-green-600 mb-2">
                  {Number(marketStats?.market_overview?.gainers ?? 0).toLocaleString()}
                </div>
                <div className="text-sm sm:text-base text-gray-600">Winning Opportunities</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold text-purple-600 mb-2">
                  1M+
                </div>
                <div className="text-sm sm:text-base text-gray-600">Alerts Sent This Month</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold text-orange-600 mb-2">
                  99.9%
                </div>
                <div className="text-sm sm:text-base text-gray-600">Data Accuracy Rate</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section with Expandable Details */}
      <section className="py-16 sm:py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12 sm:mb-20">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4 sm:mb-6">
              Everything You Need to Dominate the Markets
            </h2>
            <p className="text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto">
              Professional-grade tools that give you the competitive edge
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-8 sm:gap-12">
            {features.map((feature, index) => (
              <Collapsible key={index} className="group">
                <Card className="hover:shadow-2xl transition-all duration-300 border-l-4 border-l-blue-500">
                  <CollapsibleTrigger className="w-full text-left">
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 sm:w-16 sm:h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                            {feature.icon}
                          </div>
                          <div>
                            <CardTitle className="text-lg sm:text-2xl mb-2">{feature.title}</CardTitle>
                            <CardDescription className="text-base sm:text-lg text-gray-600">
                              {feature.description}
                            </CardDescription>
                          </div>
                        </div>
                        <ChevronDown className="h-6 w-6 text-gray-400 group-data-[state=open]:rotate-180 transition-transform" />
                      </div>
                    </CardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <CardContent className="pt-0">
                      <p className="text-gray-700 text-base sm:text-lg leading-relaxed pl-16 sm:pl-20">
                        {feature.details}
                      </p>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section (lazy) */}
      <Suspense fallback={null}>
        <TestimonialsSection testimonials={testimonials} />
      </Suspense>

      {/* Pricing Section */}
      <section className="py-16 sm:py-24 bg-gradient-to-br from-blue-900 to-blue-800 text-white">
        <div className="container mx-auto px-4">
          {/* TRIAL banner */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-6 py-3 rounded-full font-bold text-lg">
              <Zap className="h-5 w-5 mr-2" />
              TRIAL: 7-Day Free Trial on All Paid Plans
            </div>
          </div>
          
          <div className="text-center mb-12 sm:mb-20">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6">
              Start Your Trading Journey Today
            </h2>
            <p className="text-xl sm:text-2xl text-blue-100 mb-6 sm:mb-8">
              Choose the plan that fits your trading style
            </p>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 max-w-7xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className={`relative hover:scale-105 transition-transform duration-300 ${plan.popular ? 'ring-4 ring-yellow-400 scale-105' : ''} ${plan.isFree ? 'order-last lg:order-none' : ''}`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-yellow-900 px-4 py-1">
                    Most Popular
                  </Badge>
                )}
                <CardContent className="p-6 sm:p-8 text-center text-gray-900">
                  <h3 className="text-xl sm:text-2xl font-bold mb-4">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-3xl sm:text-5xl font-bold">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                  <p className="text-gray-600 mb-6 sm:mb-8">{plan.description}</p>
                  
                  <ul className="space-y-2 sm:space-y-3 mb-6 sm:mb-8 text-left">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-center">
                        <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-green-500 mr-2 sm:mr-3 flex-shrink-0" />
                        <span className="text-sm sm:text-base">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Button asChild className="w-full text-base sm:text-lg py-4 sm:py-6 bg-blue-600 hover:bg-blue-700">
                    <Link to="/auth/sign-up">
                      {plan.cta}
                      <ArrowRight className="h-4 w-4 sm:h-5 sm:w-5 ml-2" />
                    </Link>
                  </Button>
                  
                  {!plan.isFree && (
                    <p className="text-xs text-gray-500 text-center mt-3">
                      TRIAL: Start with 7-day free trial
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section (lazy) */}
      <Suspense fallback={null}>
        <HomeFAQ faqs={faqs} />
      </Suspense>

      {/* Final CTA Section */}
      <section className="py-16 sm:py-24 bg-gradient-to-br from-green-600 to-green-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-5xl font-bold mb-6 sm:mb-8">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-xl sm:text-2xl text-green-100 mb-8 sm:mb-12 max-w-3xl mx-auto">
            Join 50,000+ successful traders who rely on our platform for profitable trading decisions.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center mb-8 sm:mb-12">
            <Button asChild size="lg" variant="secondary" className="text-lg sm:text-xl px-8 sm:px-12 py-4 sm:py-6 h-auto bg-white text-green-700 hover:bg-gray-100">
              <Link to="/auth/sign-up">
                <Play className="h-5 w-5 sm:h-6 sm:w-6 mr-2 sm:mr-3" />
                Try Now for Free
                <ArrowRight className="h-5 w-5 sm:h-6 sm:w-6 ml-2 sm:ml-3" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-lg sm:text-xl px-8 sm:px-12 py-4 sm:py-6 h-auto border-white text-white hover:bg-white hover:text-green-700">
              <Link to="/pricing">
                <DollarSign className="h-5 w-5 sm:h-6 sm:w-6 mr-2 sm:mr-3" />
                View All Plans
              </Link>
            </Button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-8 text-base sm:text-lg">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 mr-2" />
              No Setup Fees
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 mr-2" />
              Cancel Anytime
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 mr-2" />
              Email Support
            </div>
          </div>
        </div>
      </section>

      {/* Exit Intent Modal */}
      {showExitIntent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Before you go — get free trading tips</h3>
              <button
                aria-label="Close"
                className="text-gray-400 hover:text-gray-600"
                onClick={() => setShowExitIntent(false)}
              >
                ×
              </button>
            </div>
            <p className="text-gray-600 mb-4">Join 50,000+ traders. Get a free screener template, $1 trial instructions, and referral 50% off tips.</p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const email = (e.currentTarget.elements.namedItem('exit_email')?.value || '').toString();
                if (!email) return;
                try { window.history.replaceState({}, '', window.location.pathname); } catch(e) {}
                setShowExitIntent(false);
                window.location.assign(`/auth/sign-up?email=${encodeURIComponent(email)}`);
              }}
              className="flex gap-2"
            >
              <input
                type="email"
                name="exit_email"
                placeholder="Enter your email"
                required
                className="flex-1 px-4 py-3 rounded-md border border-gray-300"
              />
              <Button type="submit" className="px-5">Get Started</Button>
            </form>
            <p className="text-xs text-gray-500 mt-3">No spam. Unsubscribe anytime.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;