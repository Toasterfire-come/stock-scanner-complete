import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
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
  CheckCircle
} from "lucide-react";
import { getMarketStats, getTrending } from "../api/client";

const Home = () => {
  const [marketStats, setMarketStats] = useState(null);
  const [trending, setTrending] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsResponse, trendingResponse] = await Promise.all([
          getMarketStats(),
          getTrending()
        ]);
        
        setMarketStats(statsResponse);
        setTrending(trendingResponse);
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
      description: "Filter stocks by 50+ technical and fundamental criteria with real-time data."
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Market Analysis",
      description: "Comprehensive market overview with heatmaps, sector analysis, and trend detection."
    },
    {
      icon: <Bell className="h-6 w-6" />,
      title: "Smart Alerts",
      description: "Price alerts, volume spikes, and custom notifications delivered instantly."
    },
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "Portfolio Tracking",
      description: "Track your investments with detailed analytics and performance metrics."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Risk Management",
      description: "Advanced risk metrics and position sizing tools for safer trading."
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Real-time Data",
      description: "Live market data with millisecond latency for professional trading."
    }
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Day Trader",
      content: "This platform has revolutionized my trading strategy. The screening tools are incredibly powerful.",
      rating: 5
    },
    {
      name: "Michael Chen",
      role: "Portfolio Manager",
      content: "Best stock analysis platform I've used. The real-time alerts have saved me from multiple losses.",
      rating: 5
    },
    {
      name: "Emily Rodriguez",
      role: "Investment Advisor",
      content: "My clients love the detailed reports and easy-to-understand visualizations.",
      rating: 5
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-4">
              <Star className="h-4 w-4 mr-1" />
              #1 Stock Analysis Platform
            </Badge>
            
            <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 mb-6">
              Professional Stock
              <span className="text-blue-600"> Analysis </span>
              Made Simple
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Discover winning trades with our advanced screening tools, real-time market data, 
              and AI-powered insights. Join thousands of successful traders.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="text-lg px-8">
                <Link to="/auth/sign-up">
                  Start Free Trial
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="text-lg px-8">
                <Link to="/app/stocks">
                  View Live Data
                </Link>
              </Button>
            </div>
            
            <div className="flex items-center justify-center gap-6 mt-8 text-sm text-gray-600">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                No credit card required
              </div>
              <div className="flex items-center">
                <Users className="h-4 w-4 text-blue-500 mr-2" />
                50,000+ active traders
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Market Stats Section */}
      {!isLoading && marketStats && (
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Live Market Overview</h2>
              <p className="text-gray-600">Real-time market statistics and trending stocks</p>
            </div>
            
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {marketStats.market_overview.total_stocks.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Stocks</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {marketStats.market_overview.gainers.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Gainers</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {marketStats.market_overview.losers.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Losers</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-gray-600">
                    {marketStats.market_overview.unchanged.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Unchanged</div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need for Successful Trading
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Professional-grade tools and insights that give you the edge in today's markets
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Trusted by Professional Traders
            </h2>
            <p className="text-xl text-gray-600">
              See what our community is saying about Stock Scanner
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-4">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-500">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Take Your Trading to the Next Level?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of successful traders who rely on our platform for their daily trading decisions.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" variant="secondary" className="text-lg px-8">
              <Link to="/auth/sign-up">
                Start Your Free Trial
                <ArrowRight className="h-5 w-5 ml-2" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-lg px-8 text-white border-white hover:bg-white hover:text-blue-600">
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

export default Home;