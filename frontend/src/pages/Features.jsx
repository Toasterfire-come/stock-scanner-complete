import React, { useState, useEffect } from "react";
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
  Cloud,
  CheckCircle,
  ArrowRight
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { api, publicApi } from "../api/client";

const Features = () => {
  const [platformStats, setPlatformStats] = useState(null);

  useEffect(() => {
    const fetchPlatformStats = async () => {
      try {
        const { data } = await publicApi.get('/platform-stats');
        setPlatformStats(data);
      } catch (error) {
        console.error("Failed to fetch platform stats:", error);
      }
    };

    fetchPlatformStats();
  }, []);

  const mainFeatures = [
    {
      icon: <Search className="h-8 w-8" />,
      title: "NYSE + NASDAQ Stock Screening",
      description: `Screen 10,500+ NYSE and NASDAQ stocks with 14 technical and fundamental criteria including real-time data analysis.`,
      details: [
        "Complete NYSE + NASDAQ market coverage (10,500+ stocks)",
        "7 Technical Indicators: RSI, MACD, Moving Average, Bollinger Bands, Stochastic, Volume, Price Change", 
        "7 Fundamental Indicators: Market Cap, P/E Ratio, EPS Growth, Revenue Growth, Dividend Yield, Beta, Price Range",
        "Custom filter combinations with saved presets",
        "Real-time data processing and updates",
        "Export results for further analysis"
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
        "Email and push notification delivery",
        "Custom alert conditions",
        "Alert history and management"
      ]
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Portfolio Analytics",
      description: "Track performance with professional analytics tools.",
      details: [
        "Real-time portfolio valuation",
        "Performance tracking and analysis",
        "Position management and monitoring",
        "Profit/loss calculations",
        "Portfolio diversification insights",
        "Historical performance data"
      ]
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Market Intelligence",
      description: "Real-time insights and market trend analysis.",
      details: [
        "Market trend identification",
        "Stock performance analysis",
        "Volume and price momentum tracking",
        "Market sector performance",
        "Top movers and active stocks",
        "Market condition indicators"
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
      title: "Market Overview",
      description: "Visual representation of market performance"
    },
    {
      icon: <Cloud className="h-6 w-6" />,
      title: "Cloud Sync",
      description: "Access your data from anywhere"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 dark:from-gray-900 dark:to-gray-950">
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Zap className="h-4 w-4 mr-2" />
              Professional Trading Platform
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-8 leading-tight">
              Powerful Features for
              <span className="text-blue-600 block">Serious Traders</span>
            </h1>
            
            <p className="text-2xl text-gray-700 dark:text-gray-300 mb-12 leading-relaxed">
              Everything you need to analyze markets, manage risk, and execute winning trades
              with confidence and precision.
            </p>
            
            <Button asChild size="lg" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Try Now for Free
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-24 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6">
              Core Features
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
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
                          <CardDescription className="text-lg text-gray-600 dark:text-gray-400 mt-2">
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
                            <span className="text-gray-700 dark:text-gray-300">{detail}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
                <div className="lg:w-1/2">
                  <div className="rounded-2xl overflow-hidden border bg-white dark:bg-gray-800">
                    <img
                      src={`/react/screenshots/${feature.title.toLowerCase().replace(/[^a-z0-9]+/g,'-')}.webp`}
                      alt={`${feature.title} screenshot`}
                      className="w-full h-64 object-cover"
                      loading="lazy"
                      onError={(e)=>{ e.currentTarget.src='/hero.webp'; e.currentTarget.classList.add('object-contain','bg-gray-50'); }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Features Grid */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-6">
              Additional Features
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400">
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
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{feature.title}</h3>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">{feature.description}</p>
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
              Your data and trading information are protected with industry-standard security
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <CardContent className="p-8">
                <Shield className="h-16 w-16 text-blue-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Secure Data</h3>
                <p className="text-gray-600">
                  All data is encrypted and protected using industry-standard security practices.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Clock className="h-16 w-16 text-green-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Reliable Service</h3>
                <p className="text-gray-600">
                  Our infrastructure is designed for reliability and consistent performance.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Cloud className="h-16 w-16 text-purple-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Real-Time Data</h3>
                <p className="text-gray-600">
                  Access to current market information to support your trading decisions.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-8">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl mb-12 max-w-2xl mx-auto">
            Start your 7-day trial for just $1 and see how Trade Scan Pro can transform your trading strategy.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Button asChild size="lg" variant="secondary" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Try Now for Free
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