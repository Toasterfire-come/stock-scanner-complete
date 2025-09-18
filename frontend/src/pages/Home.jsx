import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../components/ui/collapsible";
import EnhancedButton from "../components/ui/enhanced-button";
import { EnhancedCard, EnhancedCardHeader, EnhancedCardContent } from "../components/ui/enhanced-card";
import { LoadingSkeleton, LoadingSpinner } from "../components/ui/enhanced-loading";
import useScrollReveal from "../hooks/useScrollReveal";
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
  Sparkles,
  Activity,
  PieChart,
  LineChart,
  Globe,
  Lock,
  BookOpen
} from "lucide-react";
import { getMarketStatsSafe } from "../api/client";

const Home = () => {
  const [marketStats, setMarketStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

  // Scroll reveal refs
  const heroRef = useScrollReveal();
  const statsRef = useScrollReveal();
  const featuresRef = useScrollReveal();
  const testimonialsRef = useScrollReveal();
  const pricingRef = useScrollReveal();
  const faqRef = useScrollReveal();

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
      icon: <Search className="h-8 w-8" />,
      title: "Advanced Stock Screening",
      description: "Filter through thousands of stocks with comprehensive technical and fundamental criteria.",
      details: "Our professional screening engine processes extensive data to help you find investment opportunities with institutional-grade precision and comprehensive filtering options.",
      gradient: "from-blue-500 to-blue-600"
    },
    {
      icon: <Bell className="h-8 w-8" />,
      title: "Real-Time Alerts",
      description: "Never miss a trading opportunity with instant price and volume alerts.",
      details: "Set custom alerts for price movements, volume spikes, news events, and technical indicators. Get notified via email with reliable and timely notifications.",
      gradient: "from-green-500 to-green-600"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Portfolio Analytics",
      description: "Track performance with professional-grade portfolio management tools.",
      details: "Comprehensive risk metrics, performance tracking, sector allocation analysis, and detailed profit/loss tracking with professional reporting and export capabilities.",
      gradient: "from-purple-500 to-purple-600"
    },
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: "Comprehensive Documentation",
      description: "Extensive documentation and guides for all platform features and trading strategies.",
      details: "Professional documentation with step-by-step guides, best practices, API references, and comprehensive support materials to help you maximize your trading success.",
      gradient: "from-orange-500 to-orange-600"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Professional Day Trader",
      company: "Peak Capital Trading",
      content: "Trade Scan Pro has completely transformed my trading strategy. The screening tools are incredibly powerful and have helped me identify winning trades that I would have missed otherwise. The documentation is excellent.",
      rating: 5,
      profit: "Improved Strategy Results",
      avatar: "SC"
    },
    {
      name: "Michael Rodriguez",
      role: "Portfolio Manager",
      company: "Evergreen Investments",
      content: "The professional-grade analytics and risk management tools are outstanding. The platform's reliability and accuracy are excellent. Our fund's performance has improved since we started using Trade Scan Pro.",
      rating: 5,
      profit: "Enhanced Performance",
      avatar: "MR"
    },
    {
      name: "Jennifer Park",
      role: "Investment Advisor",
      company: "Wealth Strategies LLC",
      content: "My clients love the detailed reports and easy-to-understand visualizations. It's become an essential tool for our investment process. The professional presentations help me serve clients better.",
      rating: 5,
      profit: "Better Client Service",
      avatar: "JP"
    }
  ];

  const faqs = [
    {
      question: "How accurate is your market data?",
      answer: "Our data is sourced directly from major exchanges and updated in real-time with excellent uptime. We maintain professional-grade data quality through multiple validation layers, redundant connections, and advanced error correction algorithms."
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Yes, you can cancel your subscription at any time with no penalties or cancellation fees. There are no long-term contracts. Your subscription will remain active until the end of your current billing period, and you'll retain access to all features."
    },
    {
      question: "Do you offer API access?",
      answer: "Yes! Our professional plans include REST API access with comprehensive documentation, allowing you to integrate our data into your own applications, trading systems, and investment platforms."
    },
    {
      question: "What's the difference between plans?",
      answer: "Plans differ in features and support levels. Our Bronze plan is perfect for casual traders, Silver for active traders with advanced screening, and Gold for professional traders with full access and priority support."
    },
    {
      question: "Do you provide investment advice?",
      answer: "No, we provide data analysis tools and market intelligence only. All investment decisions should be made based on your own research and consultation with qualified financial advisors. We are a technology platform, not a registered investment advisor."
    },
    {
      question: "How secure is my data?",
      answer: "We employ professional-level security with SSL encryption, regular security audits, and industry-standard security measures. Your personal information and trading data are protected and are never shared with third parties."
    }
  ];

  const pricingPlans = [
    {
      name: "Bronze",
      price: "$24.99",
      period: "/month",
      description: "Perfect for individual traders getting started",
      features: [
        "Professional stock scanner & lookup",
        "Email alerts & notifications",
        "Basic portfolio tracking",
        "Documentation access",
        "Email support"
      ],
      popular: false,
      cta: "Start $1 Trial (7 Days)",
      gradient: "from-gray-100 to-gray-200",
      textColor: "text-gray-900"
    },
    {
      name: "Silver", 
      price: "$39.99",
      period: "/month",
      description: "Advanced tools for serious traders",
      features: [
        "Advanced filtering & screening",
        "Historical data access",
        "Custom watchlists (unlimited)",
        "Priority email support",
        "Advanced charting tools",
        "Export capabilities (PDF/CSV)"
      ],
      popular: true,
      cta: "Start $1 Trial (7 Days)",
      gradient: "from-blue-500 to-blue-600",
      textColor: "text-white"
    },
    {
      name: "Gold",
      price: "$89.99", 
      period: "/month",
      description: "Ultimate professional trading experience",
      features: [
        "All premium features included",
        "Real-time streaming data",
        "Full REST API access",
        "Priority phone support",
        "Professional reporting",
        "Dedicated account support"
      ],
      popular: false,
      cta: "Start $1 Trial (7 Days)",
      gradient: "from-yellow-400 to-yellow-500",
      textColor: "text-gray-900"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section - Enhanced with Modern Design */}
      <section 
        ref={heroRef}
        className="relative overflow-hidden py-20 sm:py-32 bg-gradient-to-br from-blue-50/50 via-indigo-50/30 to-purple-50/50 reveal-on-scroll"
      >
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-32 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-32 w-96 h-96 bg-gradient-to-br from-green-400/20 to-blue-400/20 rounded-full blur-3xl" />
        </div>

        <div className="container-enhanced relative">
          <div className="text-center max-w-6xl mx-auto">
            <div className="animate-fade-in">
              <Badge variant="secondary" className="mb-8 text-lg px-6 py-3 bg-white/80 backdrop-blur-sm border border-blue-200/50 hover-lift">
                <Award className="h-5 w-5 mr-3 text-blue-600" />
                Trusted by Professional Traders Worldwide
              </Badge>
            </div>
            
            <div className="animate-fade-in delay-200">
              <h1 className="typography-display-1 mb-8 leading-tight">
                Turn Market Data Into
                <span className="block text-gradient bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800">
                  Profitable Trades
                </span>
              </h1>
            </div>
            
            <div className="animate-fade-in delay-400">
              <p className="typography-body-large mb-12 max-w-4xl mx-auto text-gray-700">
                Join successful traders using our advanced screening tools, 
                real-time alerts, and comprehensive documentation to maximize their returns 
                with professional-grade precision and extensive support.
              </p>
            </div>
            
            {/* Enhanced CTA Buttons */}
            <div className="animate-fade-in delay-500 flex flex-col sm:flex-row gap-6 justify-center mb-16">
              <EnhancedButton 
                variant="primary" 
                size="xl" 
                className="group shadow-2xl hover:shadow-blue-500/25 transition-all duration-500 bg-gradient-to-r from-blue-600 to-blue-700"
                icon={<Play className="h-6 w-6" />}
              >
                <Link to="/auth/sign-up" className="flex items-center">
                  Start $1 Trial (7 Days)
                  <ArrowRight className="h-6 w-6 ml-3 group-hover:translate-x-1 transition-transform" />
                </Link>
              </EnhancedButton>
              
              <EnhancedButton 
                variant="outline" 
                size="xl" 
                className="group backdrop-blur-sm bg-white/80 border-2 border-blue-200 hover:bg-blue-50"
                icon={<BarChart3 className="h-6 w-6" />}
              >
                <Link to="/app/stocks" className="flex items-center">
                  View Live Demo
                  <Sparkles className="h-6 w-6 ml-3 group-hover:rotate-12 transition-transform" />
                </Link>
              </EnhancedButton>
            </div>
            
            {/* Enhanced Trust Indicators */}
            <div className="animate-fade-in delay-700 flex flex-wrap items-center justify-center gap-8 text-lg text-gray-600">
              {[
                { icon: CheckCircle, text: "Professional Grade Tools", color: "text-green-500" },
                { icon: Shield, text: "Secure & Reliable", color: "text-blue-500" },
                { icon: Clock, text: "Cancel Anytime", color: "text-purple-500" },
                { icon: BookOpen, text: "Extensive Documentation", color: "text-orange-500" }
              ].map((item, index) => (
                <div key={index} className="flex items-center hover-lift cursor-default">
                  <item.icon className={`h-6 w-6 mr-3 ${item.color}`} />
                  <span className="font-medium">{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Live Stats Section - Enhanced */}
      <section 
        ref={statsRef}
        className="py-20 bg-white border-y border-gray-100 reveal-on-scroll"
      >
        <div className="container-enhanced">
          {marketStats ? (
            <div className="text-center mb-16">
              <h2 className="typography-headline-1 mb-6 text-gray-900">
                Live Market Performance
              </h2>
              <p className="typography-body-medium text-gray-600 mb-12">
                Real-time data powering professional trading decisions
              </p>
              
              <div className="grid md:grid-cols-4 gap-8">
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-blue-600 mb-3">
                      {marketStats.market_overview.total_stocks.toLocaleString()}
                    </div>
                    <div className="text-gray-600 font-medium">Stocks Analyzed Today</div>
                    <div className="mt-4 flex justify-center">
                      <BarChart3 className="h-8 w-8 text-blue-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-green-600 mb-3">
                      {marketStats.market_overview.gainers.toLocaleString()}
                    </div>
                    <div className="text-gray-600 font-medium">Winning Opportunities</div>
                    <div className="mt-4 flex justify-center">
                      <TrendingUp className="h-8 w-8 text-green-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-purple-600 mb-3">
                      99.9%
                    </div>
                    <div className="text-gray-600 font-medium">Platform Uptime</div>
                    <div className="mt-4 flex justify-center">
                      <Shield className="h-8 w-8 text-purple-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-orange-600 mb-3">
                      Professional
                    </div>
                    <div className="text-gray-600 font-medium">Grade Analytics</div>
                    <div className="mt-4 flex justify-center">
                      <Target className="h-8 w-8 text-orange-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
              </div>
            </div>
          ) : (
            <div className="text-center mb-16">
              <h2 className="typography-headline-1 mb-6 text-gray-900">
                Professional Trading Platform
              </h2>
              <p className="typography-body-medium text-gray-600 mb-12">
                Trusted by professional traders for reliable market analysis
              </p>
              
              <div className="grid md:grid-cols-4 gap-8">
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-blue-600 mb-3">
                      Professional
                    </div>
                    <div className="text-gray-600 font-medium">Grade Tools</div>
                    <div className="mt-4 flex justify-center">
                      <BarChart3 className="h-8 w-8 text-blue-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-green-600 mb-3">
                      Real-Time
                    </div>
                    <div className="text-gray-600 font-medium">Market Data</div>
                    <div className="mt-4 flex justify-center">
                      <TrendingUp className="h-8 w-8 text-green-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-purple-600 mb-3">
                      Comprehensive
                    </div>
                    <div className="text-gray-600 font-medium">Documentation</div>
                    <div className="mt-4 flex justify-center">
                      <BookOpen className="h-8 w-8 text-purple-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
                
                <EnhancedCard className="text-center hover-lift">
                  <EnhancedCardContent className="p-8">
                    <div className="text-5xl font-bold text-orange-600 mb-3">
                      Expert
                    </div>
                    <div className="text-gray-600 font-medium">Support Team</div>
                    <div className="mt-4 flex justify-center">
                      <Target className="h-8 w-8 text-orange-500 opacity-50" />
                    </div>
                  </EnhancedCardContent>
                </EnhancedCard>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Section - Enhanced with Interactive Cards */}
      <section 
        ref={featuresRef}
        className="py-24 bg-gradient-to-br from-gray-50 to-blue-50/30 reveal-on-scroll"
      >
        <div className="container-enhanced">
          <div className="text-center mb-20">
            <h2 className="typography-display-2 mb-8 text-gray-900">
              Everything You Need to
              <span className="text-gradient block">Excel in Trading</span>
            </h2>
            <p className="typography-body-large max-w-3xl mx-auto text-gray-600">
              Professional-grade tools with comprehensive documentation and expert support
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-12">
            {features.map((feature, index) => (
              <Collapsible key={index} className="group">
                <EnhancedCard className="hover:shadow-2xl transition-all duration-500 border-l-4 border-l-blue-500 overflow-hidden">
                  <CollapsibleTrigger className="w-full text-left">
                    <EnhancedCardHeader className="pb-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-6">
                          <div className={`w-20 h-20 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center text-white shadow-lg`}>
                            {feature.icon}
                          </div>
                          <div className="flex-1">
                            <CardTitle className="typography-headline-3 mb-3 group-hover:text-blue-600 transition-colors">
                              {feature.title}
                            </CardTitle>
                            <CardDescription className="typography-body-medium text-gray-600">
                              {feature.description}
                            </CardDescription>
                          </div>
                        </div>
                        <ChevronDown className="h-6 w-6 text-gray-400 group-data-[state=open]:rotate-180 transition-transform duration-300 flex-shrink-0" />
                      </div>
                    </EnhancedCardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <EnhancedCardContent className="pt-0">
                      <div className="pl-26 pr-8">
                        <p className="typography-body-medium text-gray-700 leading-relaxed mb-6">
                          {feature.details}
                        </p>
                        <EnhancedButton variant="outline" size="sm" className="group">
                          Learn more
                          <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                        </EnhancedButton>
                      </div>
                    </EnhancedCardContent>
                  </CollapsibleContent>
                </EnhancedCard>
              </Collapsible>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section - Enhanced */}
      <section 
        ref={testimonialsRef}
        className="py-24 bg-white reveal-on-scroll"
      >
        <div className="container-enhanced">
          <div className="text-center mb-20">
            <h2 className="typography-display-2 mb-8 text-gray-900">
              Success Stories From Our
              <span className="text-gradient block">Trading Community</span>
            </h2>
            <p className="typography-body-large text-gray-600">
              Real results from real traders using Trade Scan Pro to enhance their trading performance
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <EnhancedCard key={index} className="hover:shadow-2xl transition-all duration-500 border-t-4 border-t-green-500 group">
                <EnhancedCardContent className="p-8">
                  <div className="flex mb-6">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-6 w-6 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  
                  <blockquote className="typography-body-medium text-gray-700 mb-8 leading-relaxed italic">
                    "{testimonial.content}"
                  </blockquote>
                  
                  <div className="border-t pt-6">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-lg mr-4">
                        {testimonial.avatar}
                      </div>
                      <div>
                        <div className="font-bold text-xl text-gray-900">{testimonial.name}</div>
                        <div className="text-gray-600 mb-1">{testimonial.role}</div>
                        <div className="text-sm text-gray-500">{testimonial.company}</div>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800 font-semibold">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      {testimonial.profit}
                    </Badge>
                  </div>
                </EnhancedCardContent>
              </EnhancedCard>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section - Enhanced */}
      <section 
        ref={pricingRef}
        className="py-24 bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900 text-white reveal-on-scroll"
      >
        <div className="container-enhanced">
          <div className="text-center mb-20">
            <h2 className="typography-display-2 mb-8 text-white">
              Start Your Trading Journey Today
            </h2>
            <p className="typography-body-large text-blue-100 mb-8">
              Choose the plan that fits your trading style and goals
            </p>
            <div className="inline-flex items-center bg-yellow-500 text-yellow-900 px-8 py-4 rounded-full font-bold text-lg shadow-lg">
              <Zap className="h-6 w-6 mr-3" />
              $1 Trial for 7 Days - No Credit Card Required
            </div>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <EnhancedCard 
                key={index} 
                className={`
                  relative hover:scale-105 transition-all duration-500 overflow-hidden
                  ${plan.popular ? 'ring-4 ring-yellow-400 scale-105 shadow-2xl' : 'shadow-xl'}
                `}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <Badge className="bg-yellow-500 text-yellow-900 px-6 py-2 text-sm font-bold shadow-lg">
                      <Star className="h-4 w-4 mr-2 fill-current" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <div className={`absolute inset-0 bg-gradient-to-br ${plan.gradient} opacity-10`} />
                
                <EnhancedCardContent className={`p-8 text-center relative z-10 ${plan.textColor}`}>
                  <h3 className="typography-headline-2 mb-6">{plan.name}</h3>
                  <div className="mb-6">
                    <span className="text-6xl font-bold">{plan.price}</span>
                    <span className="text-xl text-gray-600">{plan.period}</span>
                  </div>
                  <p className="typography-body-medium text-gray-600 mb-8">{plan.description}</p>
                  
                  <ul className="space-y-4 mb-10 text-left">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start">
                        <CheckCircle className={`h-5 w-5 ${plan.name === 'Silver' ? 'text-blue-400' : 'text-green-500'} mr-3 flex-shrink-0 mt-0.5`} />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <EnhancedButton 
                    variant={plan.popular ? "primary" : "outline"} 
                    size="lg" 
                    className="w-full group"
                  >
                    <Link to="/auth/sign-up" className="flex items-center justify-center">
                      {plan.cta}
                      <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </EnhancedButton>
                </EnhancedCardContent>
              </EnhancedCard>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section - Enhanced */}
      <section 
        ref={faqRef}
        className="py-24 bg-gray-50 reveal-on-scroll"
      >
        <div className="container-enhanced">
          <div className="text-center mb-20">
            <h2 className="typography-display-2 mb-8 text-gray-900">
              Frequently Asked
              <span className="text-gradient block">Questions</span>
            </h2>
            <p className="typography-body-large text-gray-600">
              Everything you need to know about getting started with professional trading tools
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto space-y-6">
            {faqs.map((faq, index) => (
              <Collapsible 
                key={index} 
                open={openFaq === index}
                onOpenChange={() => setOpenFaq(openFaq === index ? null : index)}
              >
                <EnhancedCard className="hover:shadow-lg transition-all duration-300">
                  <CollapsibleTrigger className="w-full text-left">
                    <EnhancedCardHeader className="flex flex-row items-center justify-between space-y-0 py-6">
                      <h3 className="typography-headline-3 pr-8">{faq.question}</h3>
                      <ChevronDown className={`h-6 w-6 text-gray-400 transition-transform duration-300 flex-shrink-0 ${openFaq === index ? 'rotate-180' : ''}`} />
                    </EnhancedCardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <EnhancedCardContent className="pt-0 pb-6">
                      <p className="typography-body-medium text-gray-700 leading-relaxed">{faq.answer}</p>
                    </EnhancedCardContent>
                  </CollapsibleContent>
                </EnhancedCard>
              </Collapsible>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section - Enhanced */}
      <section className="py-24 bg-gradient-to-br from-green-600 via-green-700 to-emerald-800 text-white relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-400/20 rounded-full blur-3xl" />
        </div>

        <div className="container-enhanced text-center relative z-10">
          <h2 className="typography-display-1 mb-8 text-white">
            Ready to Transform Your Trading?
          </h2>
          <p className="typography-body-large mb-12 max-w-3xl mx-auto text-green-100">
            Join successful traders who rely on our platform for professional trading decisions.
            Start your journey with comprehensive tools and documentation.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
            <EnhancedButton 
              variant="secondary" 
              size="xl" 
              className="group bg-white text-green-700 hover:bg-gray-100 shadow-2xl"
              icon={<Play className="h-6 w-6" />}
            >
              <Link to="/auth/sign-up" className="flex items-center">
                Start $1 Trial (7 Days)
                <ArrowRight className="h-6 w-6 ml-3 group-hover:translate-x-1 transition-transform" />
              </Link>
            </EnhancedButton>
            
            <EnhancedButton 
              variant="outline" 
              size="xl" 
              className="group border-white text-white hover:bg-white hover:text-green-700 backdrop-blur-sm"
              icon={<DollarSign className="h-6 w-6" />}
            >
              <Link to="/pricing" className="flex items-center">
                View All Plans
                <Sparkles className="h-6 w-6 ml-3 group-hover:rotate-12 transition-transform" />
              </Link>
            </EnhancedButton>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-8 text-lg">
            {[
              { icon: CheckCircle, text: "No Setup Fees" },
              { icon: CheckCircle, text: "Cancel Anytime" },
              { icon: BookOpen, text: "Full Documentation" },
              { icon: Lock, text: "Secure & Private" }
            ].map((item, index) => (
              <div key={index} className="flex items-center hover-lift cursor-default">
                <item.icon className="h-6 w-6 mr-3" />
                <span className="font-medium">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;