import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { 
  Book, 
  Code, 
  Zap,
  Play,
  ExternalLink,
  ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";

const DocumentationSimple = () => {
  const sections = [
    {
      title: "Getting Started",
      description: "Quick setup and first steps",
      icon: <Play className="h-6 w-6" />,
      items: [
        "Account Setup",
        "First Login", 
        "Dashboard Overview",
        "Basic Navigation"
      ]
    },
    {
      title: "API Documentation",
      description: "Integrate with our REST API",
      icon: <Code className="h-6 w-6" />,
      items: [
        "Authentication",
        "Stock Data Endpoints",
        "Portfolio Endpoints", 
        "Rate Limits"
      ]
    },
    {
      title: "Features Guide",
      description: "Learn to use all platform features",  
      icon: <Zap className="h-6 w-6" />,
      items: [
        "Stock Screening",
        "Setting Up Alerts",
        "Portfolio Tracking",
        "Watchlists"
      ]
    },
    {
      title: "Troubleshooting",
      description: "Common issues and solutions",
      icon: <Book className="h-6 w-6" />,
      items: [
        "Login Issues",
        "Data Not Loading", 
        "API Errors",
        "Billing Questions"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Book className="h-4 w-4 mr-2" />
              Documentation
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Everything You Need to
              <span className="text-blue-600 block">Get Started</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Comprehensive guides and API references to help you 
              make the most of TradeScan Pro.
            </p>
          </div>
        </div>
      </section>

      {/* Quick Navigation */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sections.map((section, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                      {section.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{section.title}</CardTitle>
                    </div>
                  </div>
                  <p className="text-gray-600 text-sm">{section.description}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.items.map((item, i) => (
                      <li key={i} className="text-sm text-gray-600">
                        • {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Start Guide */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Quick Start Guide</h2>
              <p className="text-xl text-gray-600">
                Get up and running with TradeScan Pro in minutes
              </p>
            </div>

            <div className="space-y-8">
              {/* Step 1 */}
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      1
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">Create Your Account</h3>
                      <p className="text-gray-700 mb-4">
                        Sign up for a free account to get started. You'll have access to basic features immediately,
                        with the option to upgrade to unlock premium tools.
                      </p>
                      <Button asChild>
                        <Link to="/auth/sign-up">
                          Sign Up Now
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Step 2 */}
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      2
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">Explore the Dashboard</h3>
                      <p className="text-gray-700 mb-4">
                        Once logged in, familiarize yourself with the dashboard and navigation. 
                        Start by exploring the stock screener and market data.
                      </p>
                      <div className="bg-gray-100 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Dashboard → Markets → Stocks</span>
                          <Badge variant="secondary">Free Access</Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Step 3 */}
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      3
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">Start Screening Stocks</h3>
                      <p className="text-gray-700 mb-4">
                        Use our powerful screening tools to find stocks that match your investment criteria.
                        Set up alerts to stay informed about market movements.
                      </p>
                      <Button variant="outline">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Try Stock Screener
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Support CTA */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Need More Help?</h2>
          <p className="text-xl mb-8">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild variant="secondary">
              <Link to="/contact">
                Contact Support
              </Link>
            </Button>
            <Button asChild variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
              <Link to="/contact">
                Email Support  
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocumentationSimple;