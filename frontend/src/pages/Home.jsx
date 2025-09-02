import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
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

const Home = () => {
  const [marketStats, setMarketStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

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
  }, []);

  const features = [
    {
      icon: <Search className="h-6 w-6" />,
      title: "Advanced Stock Screening",
      description: "Filter through 10,000+ stocks with 50+ technical and fundamental criteria.",
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
      answer: "Plans differ mainly in the number of API calls per month, available features, and support level. Bronze is great for casual traders, Silver for active traders, and Gold for professional traders and institutions."
    },
    {
      question: "Do you provide investment advice?",
      answer: "No, we provide data and analytical tools only. All investment decisions should be made based on your own research and consultation with qualified financial advisors."
    }
  ];

  const stats = [
    { label: "Active Traders", value: "50,000+", icon: <Users className="h-5 w-5" /> },
    { label: "Stocks Tracked", value: "10,000+", icon: <BarChart3 className="h-5 w-5" /> },
    { label: "Daily Alerts Sent", value: "1M+", icon: <Bell className="h-5 w-5" /> },
    { label: "API Calls/Month", value: "100M+", icon: <Zap className="h-5 w-5" /> }
  ];

  const pricingPlans = [
    {
      name: "Bronze",
      price: "$24.99",
      period: "/month",
      description: "Enhanced features for active traders",
      features: [
        "1,500 API calls per month",
        "10 calls per hour limit", 
        "Full stock scanner & lookup",
        "Email alerts & notifications",
        "News sentiment analysis",
        "Basic portfolio tracking"
      ],
      popular: true,
      cta: "Start $1 Trial"
    },
    {
      name: "Silver", 
      price: "$39.99",
      period: "/month",
      description: "Professional tools for serious traders",
      features: [
        "5,000 API calls per month",
        "25 calls per hour limit",
        "Advanced filtering & screening",
        "1-year historical data",
        "Custom watchlists (10)",
        "Priority support"
      ],
      popular: false,
      cta: "Start $1 Trial"
    },
    {
      name: "Gold",
      price: "$89.99", 
      period: "/month",
      description: "Ultimate trading experience",
      features: [
        "Unlimited API calls",
        "No hourly limits",
        "All premium features",
        "Real-time alerts",
        "Full REST API access",
        "Priority phone support"
      ],
      popular: false,
      cta: "Start $1 Trial"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section - Conversion Focused */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-5xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Award className="h-4 w-4 mr-2" />
              Trusted by 50,000+ Professional Traders
            </Badge>
            
            <h1 className="text-5xl sm:text-7xl font-bold text-gray-900 mb-8 leading-tight">
              Turn Market Data Into 
              <span className="text-blue-600 block"> Profitable Trades</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 max-w-4xl mx-auto leading-relaxed">
              Join thousands of successful traders using our advanced screening tools, 
              real-time alerts, and AI-powered market intelligence to maximize their returns.
            </p>
            
            {/* Market Status */}
            <div className="mb-8 flex justify-center">
              <MarketStatus showNotice={true} />
            </div>

            {/* Primary CTA */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
              <Button asChild size="lg" className="text-xl px-12 py-6 h-auto bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800">
                <Link to="/auth/sign-up">
                  <Play className="h-6 w-6 mr-3" />
                  Start $1 Trial for 7 Days
                  <ArrowRight className="h-6 w-6 ml-3" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="text-xl px-12 py-6 h-auto border-2">
                <Link to="/contact">
                  <Mail className="h-6 w-6 mr-3" />
                  Contact Support
                </Link>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center justify-center gap-8 text-lg text-gray-600">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                Email Support Only
              </div>
              <div className="flex items-center">
                <Shield className="h-5 w-5 text-blue-500 mr-3" />
                Bank-Level Security
              </div>
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-purple-500 mr-3" />
                Cancel Anytime
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Stats */}
      {marketStats && (
        <section className="py-16 bg-white border-y">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Live Market Performance</h2>
              <p className="text-gray-600">Real-time data from our trading platform</p>
            </div>
            
            <div className="grid md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {marketStats.market_overview.total_stocks.toLocaleString()}
                </div>
                <div className="text-gray-600">Stocks Analyzed Today</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {marketStats.market_overview.gainers.toLocaleString()}
                </div>
                <div className="text-gray-600">Winning Opportunities</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">
                  1M+
                </div>
                <div className="text-gray-600">Alerts Sent This Month</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-orange-600 mb-2">
                  99.9%
                </div>
                <div className="text-gray-600">Data Accuracy Rate</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section with Expandable Details */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Everything You Need to Dominate the Markets
            </h2>
            <p className="text-2xl text-gray-600 max-w-3xl mx-auto">
              Professional-grade tools that give you the competitive edge
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-12">
            {features.map((feature, index) => (
              <Collapsible key={index} className="group">
                <Card className="hover:shadow-2xl transition-all duration-300 border-l-4 border-l-blue-500">
                  <CollapsibleTrigger className="w-full text-left">
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                            {feature.icon}
                          </div>
                          <div>
                            <CardTitle className="text-2xl mb-2">{feature.title}</CardTitle>
                            <CardDescription className="text-lg text-gray-600">
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
                      <p className="text-gray-700 text-lg leading-relaxed pl-20">
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

      {/* Testimonials Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Success Stories From Our Traders
            </h2>
            <p className="text-2xl text-gray-600">
              Real results from real traders using Trade Scan Pro
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-2xl transition-shadow duration-300 border-t-4 border-t-green-500">
                <CardContent className="p-8">
                  <div className="flex mb-6">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-6 w-6 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <blockquote className="text-lg text-gray-700 mb-6 leading-relaxed">
                    "{testimonial.content}"
                  </blockquote>
                  <div className="border-t pt-6">
                    <div className="font-bold text-xl text-gray-900">{testimonial.name}</div>
                    <div className="text-gray-600 mb-2">{testimonial.role}</div>
                    <div className="text-sm text-gray-500 mb-3">{testimonial.company}</div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      {testimonial.profit}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-gradient-to-br from-blue-900 to-blue-800 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold mb-6">
              Start Your Trading Journey Today
            </h2>
            <p className="text-2xl text-blue-100 mb-8">
              Choose the plan that fits your trading style
            </p>
            <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-6 py-3 rounded-full font-bold text-lg">
              <Zap className="h-5 w-5 mr-2" />
              7-Day Free Trial on All Plans
            </div>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className={`relative hover:scale-105 transition-transform duration-300 ${plan.popular ? 'ring-4 ring-yellow-400 scale-105' : ''}`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-yellow-900 px-4 py-1">
                    Most Popular
                  </Badge>
                )}
                <CardContent className="p-8 text-center text-gray-900">
                  <h3 className="text-2xl font-bold mb-4">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-5xl font-bold">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                  <p className="text-gray-600 mb-8">{plan.description}</p>
                  
                  <ul className="space-y-3 mb-8 text-left">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Button asChild className="w-full text-lg py-6 bg-blue-600 hover:bg-blue-700">
                    <Link to="/auth/sign-up">
                      {plan.cta}
                      <ArrowRight className="h-5 w-5 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section with Expandable Answers */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Frequently Asked Questions
            </h2>
            <p className="text-2xl text-gray-600">
              Everything you need to know about getting started
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto space-y-4">
            {faqs.map((faq, index) => (
              <Collapsible 
                key={index} 
                open={openFaq === index}
                onOpenChange={() => setOpenFaq(openFaq === index ? null : index)}
              >
                <Card className="hover:shadow-lg transition-shadow">
                  <CollapsibleTrigger className="w-full text-left">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0">
                      <h3 className="text-xl font-semibold">{faq.question}</h3>
                      <ChevronDown className={`h-6 w-6 text-gray-400 transition-transform ${openFaq === index ? 'rotate-180' : ''}`} />
                    </CardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <CardContent className="pt-0">
                      <p className="text-gray-700 text-lg leading-relaxed">{faq.answer}</p>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 bg-gradient-to-br from-green-600 to-green-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold mb-8">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-2xl text-green-100 mb-12 max-w-3xl mx-auto">
            Join 50,000+ successful traders who rely on our platform for profitable trading decisions.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <Button asChild size="lg" variant="secondary" className="text-xl px-12 py-6 h-auto bg-white text-green-700 hover:bg-gray-100">
              <Link to="/auth/sign-up">
                <Play className="h-6 w-6 mr-3" />
                Start 7-Day Free Trial
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-xl px-12 py-6 h-auto border-white text-white hover:bg-white hover:text-green-700">
              <Link to="/pricing">
                <DollarSign className="h-6 w-6 mr-3" />
                View All Plans
              </Link>
            </Button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-8 text-lg">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              No Setup Fees
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              Cancel Anytime
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              24/7 Support
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;