import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../components/ui/collapsible";
import { 
  Search,
  HelpCircle,
  BookOpen,
  MessageSquare,
  ArrowRight,
  ChevronDown,
  BarChart3,
  Bell,
  Eye,
  DollarSign,
  Target,
  Mail,
  Clock,
  Code,
  TrendingUp,
  Settings
} from "lucide-react";
import { Link } from "react-router-dom";

const Help = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [openFaq, setOpenFaq] = useState(null);

  const helpCategories = [
    {
      icon: <BookOpen className="h-6 w-6" />,
      title: "Getting Started",
      description: "Learn the basics of using Trade Scan Pro",
      link: "/docs/getting-started",
      articles: [
        { title: "Creating your first account", link: "/docs/getting-started/create-account" },
        { title: "Understanding your dashboard", link: "/docs/getting-started/dashboard" },
        { title: "Setting up your first stock screener", link: "/docs/getting-started/first-screener" },
        { title: "How to read stock data", link: "/docs/getting-started/read-data" }
      ]
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Stock Screening",
      description: "Master our advanced screening tools",
      link: "/docs/stock-screening",
      articles: [
        { title: "Advanced screening techniques", link: "/docs/stock-screening/advanced-techniques" },
        { title: "Understanding technical indicators", link: "/docs/stock-screening/technical-indicators" },
        { title: "Using fundamental filters", link: "/docs/stock-screening/fundamental-filters" },
        { title: "Saving and sharing screeners", link: "/docs/stock-screening/save-share" }
      ]
    },
    {
      icon: <Bell className="h-6 w-6" />,
      title: "Alerts & Notifications",
      description: "Set up and manage your alerts",
      link: "/docs/alerts",
      articles: [
        { title: "Creating price alerts", link: "/docs/alerts/price-alerts" },
        { title: "Volume and news alerts", link: "/docs/alerts/volume-news-alerts" },
        { title: "Managing alert settings", link: "/docs/alerts/settings" },
        { title: "Alert history and tracking", link: "/docs/alerts/history" }
      ]
    },
    {
      icon: <DollarSign className="h-6 w-6" />,
      title: "Portfolio Management",
      description: "Track and analyze your investments",
      link: "/docs/portfolio",
      articles: [
        { title: "Adding stocks to portfolio", link: "/docs/portfolio/add-stocks" },
        { title: "Portfolio analytics overview", link: "/docs/portfolio/analytics" },
        { title: "Performance tracking", link: "/docs/portfolio/performance" },
        { title: "Dividend monitoring", link: "/docs/portfolio/dividends" }
      ]
    },
    {
      icon: <Eye className="h-6 w-6" />,
      title: "Watchlists",
      description: "Organize and monitor your stocks",
      link: "/docs/watchlists",
      articles: [
        { title: "Creating custom watchlists", link: "/docs/watchlists/create" },
        { title: "Adding and removing stocks", link: "/docs/watchlists/manage" },
        { title: "Watchlist analytics", link: "/docs/watchlists/analytics" },
        { title: "Sharing watchlists", link: "/docs/watchlists/sharing" }
      ]
    },
    {
      icon: <Code className="h-6 w-6" />,
      title: "API & Integrations",
      description: "Connect Trade Scan Pro with other tools",
      link: "/docs/api",
      articles: [
        { title: "API key management", link: "/docs/api/keys" },
        { title: "API rate limits and usage", link: "/docs/api/limits" },
        { title: "Integration examples", link: "/docs/api/examples" },
        { title: "Webhook setup", link: "/docs/api/webhooks" }
      ]
    }
  ];

  const frequentlyAskedQuestions = [
    {
      question: "How do I upgrade my subscription plan?",
      answer: "You can upgrade your plan at any time by going to Account Settings > Current Plan, then selecting 'Change Plan'. The upgrade takes effect immediately and you'll be billed the prorated difference."
    },
    {
      question: "What data sources do you use for stock information?",
      answer: "We use Yahoo Finance as our primary data source for real-time stock prices, historical data, and company fundamentals. We also employ proprietary news scraping technology to provide comprehensive market coverage."
    },
    {
      question: "How accurate is your real-time data?",
      answer: "Our data is updated in real-time during market hours with a delay of less than 1 second. We source data directly from Yahoo Finance, which provides institutional-grade market data."
    },
    {
      question: "Can I export my screening results?",
      answer: "Yes! All paid plans include data export functionality. You can export your screening results, portfolio data, and watchlists in CSV, JSON, or Excel formats."
    },
    {
      question: "How do API rate limits work?",
      answer: "API calls are counted based on the complexity of the operation: Stock lookups (1 call), Stock listings (5 calls), Screeners (2 calls), Alerts (2 calls), Market data (2 calls), Watchlists (2 calls)."
    },
    {
      question: "Do you offer phone support?",
      answer: "Email support is available for all plans. We typically respond within 24 hours. For urgent issues, Gold plan subscribers get priority support."
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Yes, you can cancel your subscription at any time with no cancellation fees. Your subscription will remain active until the end of your current billing period."
    },
    {
      question: "How do I set up stock price alerts?",
      answer: "Go to the Alerts section in your dashboard, click 'Create Alert', select the stock, set your price conditions (above/below), and choose your notification preferences. You'll receive alerts via email when conditions are met."
    },
    {
      question: "What's the difference between technical and fundamental indicators?",
      answer: "Technical indicators (RSI, MACD, Moving Averages) analyze price and volume patterns. Fundamental indicators (P/E ratio, EPS, Market Cap) analyze company financial health and valuation metrics."
    },
    {
      question: "How do I track my portfolio performance?",
      answer: "Add stocks to your portfolio with purchase prices and quantities. Our system will automatically calculate your gains/losses, dividends, and performance metrics including total return and sector allocation."
    }
  ];

  const supportChannels = [
    {
      icon: <Mail className="h-6 w-6" />,
      title: "Email Support",
      description: "Get help via email",
      contact: process.env.REACT_APP_SUPPORT_EMAIL || "noreply.retailtradescanner@gmail.com",
      responseTime: "Within 24 hours"
    },
    {
      icon: <MessageSquare className="h-6 w-6" />,
      title: "Contact Form",
      description: "Send us a detailed message",
      contact: "Use our contact form",
      responseTime: "Within 24 hours",
      link: "/contact"
    },
    {
      icon: <BookOpen className="h-6 w-6" />,
      title: "Documentation",
      description: "Comprehensive guides and tutorials",
      contact: "Self-service help",
      responseTime: "Available 24/7",
      link: "/docs"
    }
  ];

  const filteredFaqs = frequentlyAskedQuestions.filter(faq =>
    searchQuery === "" ||
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="py-20 sm:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <HelpCircle className="h-4 w-4 mr-2" />
              Help Center
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              How Can We
              <span className="text-blue-600 block">Help You Today?</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Find answers, learn new features, and get the most out of Trade Scan Pro
            </p>

            {/* Search Box */}
            <div className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <Input
                  type="text"
                  placeholder="Search for help articles, FAQs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Help Categories */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Browse by Category
            </h2>
            <p className="text-xl text-gray-600">
              Find detailed guides for every feature
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {helpCategories.map((category, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                    {category.icon}
                  </div>
                  <CardTitle className="text-xl">{category.title}</CardTitle>
                  <p className="text-gray-600">{category.description}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {category.articles.slice(0, 4).map((article, articleIndex) => (
                      <li key={articleIndex}>
                        <Link 
                          to={article.link}
                          className="flex items-center text-sm text-gray-700 hover:text-blue-600 cursor-pointer"
                        >
                          <ArrowRight className="h-3 w-3 mr-2" />
                          {article.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4">
                    <Button asChild variant="outline" size="sm">
                      <Link to={category.link}>
                        View All Articles
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Quick answers to common questions
            </p>
          </div>

          <div className="max-w-4xl mx-auto space-y-4">
            {filteredFaqs.map((faq, index) => (
              <Collapsible 
                key={index} 
                open={openFaq === index}
                onOpenChange={() => setOpenFaq(openFaq === index ? null : index)}
              >
                <Card className="hover:shadow-md transition-shadow">
                  <CollapsibleTrigger className="w-full text-left">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0">
                      <h3 className="text-lg font-semibold pr-4">{faq.question}</h3>
                      <ChevronDown className={`h-6 w-6 text-gray-400 transition-transform flex-shrink-0 ${openFaq === index ? 'rotate-180' : ''}`} />
                    </CardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <CardContent className="pt-0">
                      <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>
            ))}

            {filteredFaqs.length === 0 && searchQuery && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No FAQs found matching "{searchQuery}"</p>
                <p className="text-gray-400 mt-2">Try searching with different keywords or browse our categories above</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Support Channels */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Still Need Help?
            </h2>
            <p className="text-xl text-gray-600">
              Get in touch with our support team
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {supportChannels.map((channel, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600 mx-auto mb-4">
                    {channel.icon}
                  </div>
                  <CardTitle className="text-xl">{channel.title}</CardTitle>
                  <p className="text-gray-600">{channel.description}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-800 font-medium mb-2">{channel.contact}</p>
                  <div className="flex items-center justify-center text-sm text-gray-500 mb-4">
                    <Clock className="h-4 w-4 mr-1" />
                    {channel.responseTime}
                  </div>
                  {channel.link && (
                    <Button asChild variant="outline" size="sm">
                      <Link to={channel.link}>
                        Get Help
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Link>
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Request CTA */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">
            Have a Feature Request?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            We're always looking to improve Trade Scan Pro. 
            Let us know what features would help you trade better.
          </p>
          <Button size="lg" variant="secondary" asChild>
            <Link to="/contact">
              <Mail className="h-5 w-5 mr-2" />
              Send Feature Request
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Help;