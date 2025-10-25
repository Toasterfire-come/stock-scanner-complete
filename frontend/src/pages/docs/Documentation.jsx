import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { 
  BookOpen,
  ArrowRight,
  BarChart3,
  Bell,
  Eye,
  DollarSign,
  Target,
  Code,
  TrendingUp,
  Settings,
  Users,
  Zap
} from "lucide-react";
import { Link } from "react-router-dom";

const Documentation = () => {
  const docSections = [
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: "Getting Started",
      description: "Learn the basics of using Trade Scan Pro",
      badge: "New User",
      badgeColor: "bg-green-100 text-green-800",
      articles: [
        {
          title: "Creating your first account",
          description: "Step-by-step guide to setting up your Trade Scan Pro account",
          link: "/docs/getting-started/create-account",
          readTime: "3 min"
        },
        {
          title: "Understanding your dashboard", 
          description: "Navigate and customize your main dashboard interface",
          link: "/docs/getting-started/dashboard",
          readTime: "5 min"
        },
        {
          title: "Setting up your first stock screener",
          description: "Create powerful stock screens to find trading opportunities",
          link: "/docs/getting-started/first-screener",
          readTime: "7 min"
        },
        {
          title: "How to read stock data",
          description: "Understand technical and fundamental data in our platform",
          link: "/docs/getting-started/read-data",
          readTime: "6 min"
        }
      ]
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Stock Screening",
      description: "Master our advanced screening tools",
      badge: "Advanced",
      badgeColor: "bg-blue-100 text-blue-800",
      articles: [
        {
          title: "Advanced screening techniques",
          description: "Combine multiple filters for precise stock selection",
          link: "/docs/stock-screening/advanced-techniques",
          readTime: "10 min"
        },
        {
          title: "Understanding technical indicators",
          description: "Master RSI, MACD, Bollinger Bands and more",
          link: "/docs/stock-screening/technical-indicators", 
          readTime: "12 min"
        },
        {
          title: "Using fundamental filters",
          description: "Screen by P/E ratio, market cap, revenue growth and more",
          link: "/docs/stock-screening/fundamental-filters",
          readTime: "8 min"  
        },
        {
          title: "Saving and sharing screeners",
          description: "Create templates and share with your team",
          link: "/docs/stock-screening/save-share",
          readTime: "4 min"
        }
      ]
    },
    {
      icon: <Bell className="h-8 w-8" />,
      title: "Alerts & Notifications",
      description: "Set up and manage your alerts",
      badge: "Essential", 
      badgeColor: "bg-orange-100 text-orange-800",
      articles: [
        {
          title: "Creating price alerts",
          description: "Get notified when stocks hit your target prices",
          link: "/docs/alerts/price-alerts",
          readTime: "5 min"
        },
        {
          title: "Volume and news alerts", 
          description: "Track unusual volume spikes and breaking news",
          link: "/docs/alerts/volume-news-alerts",
          readTime: "6 min"
        },
        {
          title: "Managing alert settings",
          description: "Customize notification preferences and delivery methods",
          link: "/docs/alerts/settings",
          readTime: "4 min"
        },
        {
          title: "Alert history and tracking",
          description: "Review past alerts and measure their effectiveness",
          link: "/docs/alerts/history",
          readTime: "3 min"
        }
      ]
    },
    {
      icon: <DollarSign className="h-8 w-8" />,
      title: "Portfolio Management",
      description: "Track and analyze your investments",
      badge: "Pro",
      badgeColor: "bg-purple-100 text-purple-800",
      articles: [
        {
          title: "Adding stocks to portfolio",
          description: "Input your positions and track performance",
          link: "/docs/portfolio/add-stocks",
          readTime: "4 min"
        },
        {
          title: "Portfolio analytics overview",
          description: "Understand risk metrics and performance attribution",
          link: "/docs/portfolio/analytics",
          readTime: "8 min"
        },
        {
          title: "Performance tracking",
          description: "Monitor returns, benchmark comparisons, and more",
          link: "/docs/portfolio/performance",
          readTime: "6 min"
        },
        {
          title: "Dividend monitoring",
          description: "Track dividend payments and yield analysis",
          link: "/docs/portfolio/dividends",
          readTime: "5 min"
        }
      ]
    },
    {
      icon: <Eye className="h-8 w-8" />,
      title: "Watchlists",
      description: "Organize and monitor your stocks",
      badge: "Popular",
      badgeColor: "bg-yellow-100 text-yellow-800",
      articles: [
        {
          title: "Creating custom watchlists",
          description: "Organize stocks by themes, sectors, or strategies",
          link: "/docs/watchlists/create",
          readTime: "3 min"
        },
        {
          title: "Adding and removing stocks",
          description: "Manage your watchlist contents efficiently",
          link: "/docs/watchlists/manage", 
          readTime: "2 min"
        },
        {
          title: "Watchlist analytics",
          description: "Analyze performance and trends across your lists",
          link: "/docs/watchlists/analytics",
          readTime: "7 min"
        },
        {
          title: "Sharing watchlists",
          description: "Collaborate with team members and friends",
          link: "/docs/watchlists/sharing",
          readTime: "4 min"
        }
      ]
    },
    {
      icon: <Code className="h-8 w-8" />,
      title: "API & Integrations",
      description: "Connect Trade Scan Pro with other tools",
      badge: "Developer",
      badgeColor: "bg-gray-100 text-gray-800",
      articles: [
        {
          title: "API key management",
          description: "Generate and manage your API keys securely",
          link: "/docs/api/keys",
          readTime: "4 min"
        },
        {
          title: "API rate limits and usage",
          description: "Understanding quotas and optimizing API calls",
          link: "/docs/api/limits",
          readTime: "6 min"
        },
        {
          title: "Integration examples",
          description: "Code samples for common use cases",
          link: "/docs/api/examples",
          readTime: "15 min"
        },
        {
          title: "Webhook setup",
          description: "Receive real-time data updates in your applications",
          link: "/docs/api/webhooks",
          readTime: "8 min"
        }
      ]
    }
  ];

  const popularArticles = [
    {
      title: "Setting up your first stock screener",
      category: "Getting Started",
      views: "15.2k",
      link: "/docs/getting-started/first-screener"
    },
    {
      title: "Understanding technical indicators", 
      category: "Stock Screening",
      views: "12.8k",
      link: "/docs/stock-screening/technical-indicators"
    },
    {
      title: "Creating price alerts",
      category: "Alerts",
      views: "10.5k", 
      link: "/docs/alerts/price-alerts"
    },
    {
      title: "Portfolio analytics overview",
      category: "Portfolio",
      views: "8.9k",
      link: "/docs/portfolio/analytics"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <BookOpen className="h-4 w-4 mr-2" />
              Documentation
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Complete Trading
              <span className="text-blue-600 block">Knowledge Base</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Everything you need to master Trade Scan Pro and become a more successful trader.
              From basic setup to advanced strategies.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="text-xl px-8 py-6">
                <Link to="/docs/getting-started/create-account">
                  <BookOpen className="h-6 w-6 mr-3" />
                  Start Learning
                  <ArrowRight className="h-6 w-6 ml-3" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-xl px-8 py-6">
                <Link to="/contact">
                  <Users className="h-6 w-6 mr-3" />
                  Get Support
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Articles */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Most Popular Articles</h2>
            <p className="text-xl text-gray-600">Start with what other traders find most helpful</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {popularArticles.map((article, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant="outline" className="text-xs">
                      {article.category}
                    </Badge>
                    <span className="text-xs text-gray-500">{article.views} views</span>
                  </div>
                  <Link to={article.link} className="block">
                    <h3 className="font-semibold text-gray-900 hover:text-blue-600 leading-tight">
                      {article.title}
                    </h3>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Complete Documentation
            </h2>
            <p className="text-xl text-gray-600">
              Comprehensive guides organized by feature and skill level
            </p>
          </div>
          
          <div className="space-y-12">
            {docSections.map((section, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                      {section.icon}
                    </div>
                    <div>
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-2xl font-bold text-gray-900">{section.title}</h3>
                        <Badge className={section.badgeColor}>{section.badge}</Badge>
                      </div>
                      <p className="text-gray-600 text-lg">{section.description}</p>
                    </div>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  {section.articles.map((article, articleIndex) => (
                    <Card key={articleIndex} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-3">
                          <h4 className="font-semibold text-gray-900 leading-tight flex-1 pr-4">
                            <Link to={article.link} className="hover:text-blue-600">
                              {article.title}
                            </Link>
                          </h4>
                          <span className="text-xs text-gray-500 whitespace-nowrap">{article.readTime}</span>
                        </div>
                        <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                          {article.description}
                        </p>
                        <Button asChild variant="ghost" size="sm" className="p-0 h-auto text-blue-600 hover:text-blue-700">
                          <Link to={article.link} className="flex items-center">
                            Read Article
                            <ArrowRight className="h-4 w-4 ml-1" />
                          </Link>
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Support CTA */}
      <section className="py-24 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <Zap className="h-16 w-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-6">
            Need More Help?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Can't find what you're looking for? Our support team is here to help you succeed with Trade Scan Pro.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/contact">
                Contact Support
                <ArrowRight className="h-5 w-5 ml-2" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-700" asChild>
              <Link to="/help">
                Browse FAQ
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Documentation;