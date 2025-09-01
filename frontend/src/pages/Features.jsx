import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { 
  Search, 
  Bell, 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Zap,
  Target,
  Eye,
  Clock,
  Users,
  Smartphone,
  Cloud,
  CheckCircle,
  ArrowRight
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";

const Features = () => {
  const mainFeatures = [
    {
      icon: <Search className="h-8 w-8" />,
      title: "Advanced Stock Screening",
      description: "Filter through 10,000+ stocks with 50+ technical and fundamental criteria.",
      details: [
        "Real-time screening across all major exchanges",
        "Custom filter combinations with saved presets",
        "Technical indicators: RSI, MACD, Moving Averages",
        "Fundamental metrics: P/E, EPS, Revenue Growth",
        "Sector and industry-specific screening",
        "Export results to CSV or Excel"
      ]
    },
    {
      icon: <Bell className="h-8 w-8" />,
      title: "Real-Time Alerts",
      description: "Never miss a trading opportunity with instant notifications.",
      details: [
        "Price movement alerts (% change or absolute)",
        "Volume spike notifications",
        "Technical indicator breakouts",
        "News sentiment alerts",
        "Multiple delivery methods: Email, SMS, Push",
        "Smart alert clustering to reduce noise"
      ]
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Portfolio Analytics",
      description: "Track performance with institutional-grade analytics.",
      details: [
        "Real-time portfolio valuation",
        "Risk metrics and diversification analysis",
        "Performance attribution by sector/stock",
        "Tax-loss harvesting opportunities",
        "Benchmark comparison (S&P 500, NASDAQ)",
        "Detailed profit/loss reporting"
      ]
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Market Intelligence",
      description: "AI-powered insights from news and social sentiment.",
      details: [
        "Real-time news sentiment analysis",
        "Social media trend tracking",
        "Institutional activity monitoring",
        "Earnings surprise predictions",
        "Market correlation analysis",
        "Custom intelligence feeds"
      ]
    }
  ];

  const additionalFeatures = [
    {
      icon: <Target className="h-6 w-6" />,
      title: "Watchlists",
      description: "Organize and monitor your favorite stocks"
    },
    {
      icon: <Eye className="h-6 w-6" />,
      title: "Market Heatmaps",
      description: "Visual representation of market performance"
    },

    {
      icon: <Cloud className="h-6 w-6" />,
      title: "Cloud Sync",
      description: "Access your data from anywhere"
    }
  ];

  // Brokerage integrations removed as requested

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Zap className="h-4 w-4 mr-2" />
              Professional Trading Platform
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Powerful Features for
              <span className="text-blue-600 block">Serious Traders</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Everything you need to analyze markets, manage risk, and execute winning trades
              with confidence and precision.
            </p>
            
            <Button asChild size="lg" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Start 7-Day Free Trial
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Core Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built by traders, for traders. Every feature is designed to give you an edge in the markets.
            </p>
          </div>
          
          <div className="space-y-16">
            {mainFeatures.map((feature, index) => (
              <div key={index} className={`flex flex-col lg:flex-row items-center gap-12 ${index % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
                <div className="lg:w-1/2">
                  <Card className="hover:shadow-2xl transition-shadow duration-300">
                    <CardHeader>
                      <div className="flex items-center space-x-4 mb-4">
                        <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                          {feature.icon}
                        </div>
                        <div>
                          <CardTitle className="text-3xl">{feature.title}</CardTitle>
                          <CardDescription className="text-lg text-gray-600 mt-2">
                            {feature.description}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        {feature.details.map((detail, i) => (
                          <li key={i} className="flex items-start">
                            <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700">{detail}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
                <div className="lg:w-1/2">
                  <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-8 text-white">
                    <div className="h-64 flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mb-4 mx-auto">
                          {React.cloneElement(feature.icon, { className: "h-12 w-12" })}
                        </div>
                        <p className="text-xl font-medium">Feature Preview</p>
                        <p className="text-blue-100 mt-2">Interactive demo coming soon</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Features Grid */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Additional Features
            </h2>
            <p className="text-xl text-gray-600">
              More tools to enhance your trading experience
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {additionalFeatures.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
                      <p className="text-gray-600 mt-1">{feature.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Security & Reliability */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Security & Reliability
            </h2>
            <p className="text-xl text-gray-600">
              Your data and trading information are protected with bank-level security
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardContent className="p-8">
                <Shield className="h-16 w-16 text-blue-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Bank-Level Encryption</h3>
                <p className="text-gray-600">
                  All data is encrypted using AES-256 encryption, the same standard used by major financial institutions.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Clock className="h-16 w-16 text-green-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">99.9% Uptime</h3>
                <p className="text-gray-600">
                  Our redundant infrastructure ensures your trading platform is always available when you need it.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Cloud className="h-16 w-16 text-purple-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Real-Time Data</h3>
                <p className="text-gray-600">
                  Direct feeds from major exchanges ensure you always have the most current market information.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Note: Brokerage integrations removed as requested */}

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-8">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl mb-12 max-w-2xl mx-auto">
            Start your 7-day free trial and see how Trade Scan Pro can transform your trading strategy.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Button asChild size="lg" variant="secondary" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Start Free Trial
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-xl px-12 py-6 h-auto border-white text-white hover:bg-white hover:text-blue-700">
              <Link to="/pricing">
                View Pricing
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Features;