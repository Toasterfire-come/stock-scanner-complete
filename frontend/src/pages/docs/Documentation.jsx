import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { 
  Book, 
  Search, 
  Code, 
  Zap,
  Play,
  ChevronRight,
  ExternalLink,
  Copy,
  CheckCircle,
  ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";

const Documentation = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedCode, setCopiedCode] = useState("");

  const sections = [
    {
      title: "Getting Started",
      description: "Quick setup and first steps",
      icon: <Play className="h-6 w-6" />,
      items: [
        { title: "Account Setup", href: "#account-setup" },
        { title: "First Login", href: "#first-login" },
        { title: "Dashboard Overview", href: "#dashboard" },
        { title: "Basic Navigation", href: "#navigation" }
      ]
    },
    {
      title: "API Documentation",
      description: "Integrate with our REST API",
      icon: <Code className="h-6 w-6" />,
      items: [
        { title: "Authentication", href: "#api-auth" },
        { title: "Stock Data Endpoints", href: "#stock-data" },
        { title: "Portfolio Endpoints", href: "#portfolio-api" },
        { title: "Rate Limits", href: "#rate-limits" }
      ]
    },
    {
      title: "Features Guide",
      description: "Learn to use all platform features",  
      icon: <Zap className="h-6 w-6" />,
      items: [
        { title: "Stock Screening", href: "#screening" },
        { title: "Setting Up Alerts", href: "#alerts" },
        { title: "Portfolio Tracking", href: "#portfolio" },
        { title: "Watchlists", href: "#watchlists" }
      ]
    },
    {
      title: "Troubleshooting",
      description: "Common issues and solutions",
      icon: <Book className="h-6 w-6" />,
      items: [
        { title: "Login Issues", href: "#login-issues" },
        { title: "Data Not Loading", href: "#data-issues" },
        { title: "API Errors", href: "#api-errors" },
        { title: "Billing Questions", href: "#billing" }
      ]
    }
  ];

  const quickStart = `// Quick Start Example
const apiKey = 'your_api_key_here';
const baseUrl = 'https://api.tradescanpro.com/v1';

// Get stock quote
fetch(\`\${baseUrl}/stocks/AAPL/quote\`, {
  headers: {
    'Authorization': \`Bearer \${apiKey}\`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('AAPL Quote:', data);
})
.catch(error => {
  console.error('Error:', error);
});`;

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(""), 2000);
  };

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
              Comprehensive guides, API references, and tutorials to help you 
              make the most of Trade Scan Pro.
            </p>

            {/* Search Bar */}
            <div className="relative max-w-2xl mx-auto mb-8">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input 
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 py-4 text-lg"
              />
            </div>
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
                      <li key={i}>
                        <a 
                          href={item.href}
                          className="flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors"
                        >
                          <ChevronRight className="h-3 w-3 mr-1" />
                          {item.title}
                        </a>
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
                Get up and running with Trade Scan Pro in minutes
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
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">Get Your API Key</h3>
                      <p className="text-gray-700 mb-4">
                        Once logged in, navigate to your account settings to generate your API key. 
                        This key will authenticate your requests to our API.
                      </p>
                      <div className="bg-gray-100 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Dashboard → Settings → API Keys</span>
                          <Badge variant="secondary">Premium Feature</Badge>
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
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">Make Your First API Call</h3>
                      <p className="text-gray-700 mb-4">
                        Test your integration with a simple API call to get stock data.
                      </p>
                      <div className="bg-gray-900 rounded-lg p-4 text-sm text-white font-mono relative">
                        <button 
                          onClick={() => copyToClipboard(quickStart)}
                          className="absolute top-2 right-2 p-2 hover:bg-gray-800 rounded"
                        >
                          {copiedCode === quickStart ? (
                            <CheckCircle className="h-4 w-4 text-green-400" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </button>
                        <pre className="overflow-x-auto">{quickStart}</pre>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">API Reference</h2>
              <p className="text-xl text-gray-600">
                Complete reference for all available endpoints
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Code className="h-5 w-5 mr-2" />
                    Stock Data API
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-semibold">GET /stocks/{symbol}/quote</h4>
                      <p className="text-sm text-gray-600">Get real-time quote for a stock symbol</p>
                    </div>
                    <div className="border-l-4 border-green-500 pl-4">
                      <h4 className="font-semibold">GET /stocks/screener</h4>
                      <p className="text-sm text-gray-600">Screen stocks with custom filters</p>
                    </div>
                    <div className="border-l-4 border-purple-500 pl-4">
                      <h4 className="font-semibold">GET /stocks/{symbol}/history</h4>
                      <p className="text-sm text-gray-600">Get historical price data</p>
                    </div>
                  </div>
                  <Button asChild variant="outline" className="w-full mt-6">
                    <a href="#api-reference">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View Full API Docs
                    </a>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Zap className="h-5 w-5 mr-2" />
                    Portfolio API
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-semibold">GET /portfolio</h4>
                      <p className="text-sm text-gray-600">Get portfolio overview and holdings</p>
                    </div>
                    <div className="border-l-4 border-green-500 pl-4">
                      <h4 className="font-semibold">POST /portfolio/positions</h4>
                      <p className="text-sm text-gray-600">Add or update portfolio positions</p>
                    </div>
                    <div className="border-l-4 border-purple-500 pl-4">
                      <h4 className="font-semibold">GET /portfolio/performance</h4>
                      <p className="text-sm text-gray-600">Get detailed performance metrics</p>
                    </div>
                  </div>
                  <Button asChild variant="outline" className="w-full mt-6">
                    <a href="#portfolio-api">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View Portfolio Docs
                    </a>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Anchors */}
      <div id="api-reference" className="sr-only" />

      {/* Popular Guides */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Popular Guides</h2>
            <p className="text-xl text-gray-600">
              Step-by-step tutorials for common use cases
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Setting Up Your First Screen
                </h3>
                <p className="text-gray-600 mb-4">
                  Learn how to create custom stock screens to find trading opportunities.
                </p>
                <Button variant="outline" size="sm">
                  Read Guide
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Portfolio Tracking Setup
                </h3>
                <p className="text-gray-600 mb-4">
                  Connect your brokerage account and start tracking your portfolio performance.
                </p>
                <Button variant="outline" size="sm">
                  Read Guide
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  API Integration Examples
                </h3>
                <p className="text-gray-600 mb-4">
                  Code examples and best practices for integrating our API into your applications.
                </p>
                <Button variant="outline" size="sm">
                  Read Guide
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </CardContent>
            </Card>
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
              <Link to="/docs">
                Browse Docs
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Documentation;