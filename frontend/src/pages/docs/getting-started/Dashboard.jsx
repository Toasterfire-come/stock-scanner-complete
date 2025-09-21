import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Alert, AlertDescription } from "../../../components/ui/alert";
import { 
  ArrowLeft,
  ArrowRight,
  BarChart3,
  TrendingUp,
  Eye,
  Bell,
  Settings,
  Layout,
  Clock,
  CheckCircle,
  Lightbulb,
  Target
} from "lucide-react";
import { Link } from "react-router-dom";

const Dashboard = () => {
  const dashboardSections = [
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Market Overview",
      description: "Real-time market statistics and key indices",
      features: [
        "Live market status indicator (Open/Closed)",
        "Major indices performance (S&P 500, NASDAQ, DOW)",
        "Top gainers and losers",
        "Market sentiment indicators",
        "Economic calendar events"
      ],
      tips: "Check the market status indicator first - data updates are paused when markets are closed for more accurate information."
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: "Quick Actions",
      description: "Fast access to your most-used features",
      features: [
        "Create new stock screener",
        "Add stocks to watchlist",
        "Set up price alerts",
        "View recent screening results",
        "Access saved templates"
      ],
      tips: "Pin your most frequently used screeners to the quick actions panel for faster access."
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Portfolio Summary",
      description: "Overview of your investment performance",
      features: [
        "Total portfolio value and daily change",
        "Best and worst performing positions",
        "Asset allocation breakdown",
        "Recent dividend payments",
        "Performance vs. benchmarks"
      ],
      tips: "Add your positions with accurate purchase dates and prices for more precise performance tracking."
    },
    {
      icon: <Eye className="h-8 w-8" />,
      title: "Watchlists Preview",
      description: "Quick view of your monitored stocks",
      features: [
        "Real-time prices for watchlist stocks",
        "Percentage changes and price movements",
        "Volume indicators and alerts",
        "Quick add/remove functionality",
        "Performance sorting options"
      ],
      tips: "Organize watchlists by strategy (e.g., 'Growth Stocks', 'Dividend Plays', 'Technical Breakouts') for better workflow."
    },
    {
      icon: <Bell className="h-8 w-8" />,
      title: "Alerts & Notifications",
      description: "Recent alerts and system notifications",
      features: [
        "Price alert notifications",
        "Volume spike alerts",
        "News and earnings alerts",
        "System maintenance notices",
        "Account and billing updates"
      ],
      tips: "Customize alert frequency in settings to avoid notification overload while staying informed."
    }
  ];

  const customizationOptions = [
    {
      title: "Layout Preferences",
      description: "Adjust the dashboard layout to match your trading style",
      options: [
        "Drag and drop widget rearrangement",
        "Resize widgets to emphasize important data",
        "Hide or show sections based on your needs",
        "Switch between grid and list views",
        "Create multiple dashboard layouts for different strategies"
      ]
    },
    {
      title: "Data Display Settings",
      description: "Control how market data is presented",
      options: [
        "Choose between percentage or dollar change displays",
        "Set your preferred time zones for market hours",
        "Select default chart timeframes (1D, 1W, 1M, etc.)",
        "Configure color schemes for gains/losses",
        "Set decimal precision for price displays"
      ]
    },
    {
      title: "Notification Preferences",
      description: "Manage how you receive updates and alerts",
      options: [
        "Email notification frequency settings",
        "Push notification preferences",
        "Alert sound customization",
        "Quiet hours configuration",
        "Priority alert settings"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link to="/docs">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Documentation
              </Link>
            </Button>
            <span className="text-gray-400">/</span>
            <Badge variant="outline">Getting Started</Badge>
          </div>
        </div>
      </div>

      {/* Header */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <Badge className="mb-4 bg-green-100 text-green-800">
                <Layout className="h-4 w-4 mr-2" />
                Getting Started
              </Badge>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                Understanding Your Dashboard
              </h1>
              <p className="text-xl text-gray-700 leading-relaxed">
                Your dashboard is mission control for your trading activities. Learn how to navigate,
                customize, and get the most out of every feature to make better trading decisions.
              </p>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600 mb-8">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                5 min read
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                Updated Dec 2024
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Overview */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <Alert className="border-blue-200 bg-blue-50 mb-12">
              <Lightbulb className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>First Time?</strong> Take a few minutes to explore each section. You can always customize the layout later by clicking the settings gear icon in the top right corner.
              </AlertDescription>
            </Alert>

            <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard Sections</h2>
            
            <div className="space-y-8">
              {dashboardSections.map((section, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                        {section.icon}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl text-gray-900">{section.title}</CardTitle>
                        <p className="text-gray-600 mt-1">{section.description}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">Key Features:</h4>
                    <ul className="space-y-3 mb-6">
                      {section.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Alert>
                      <Lightbulb className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Pro Tip:</strong> {section.tips}
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Customization Guide */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Customizing Your Dashboard</h2>
            <p className="text-xl text-gray-600 mb-12">
              Make your dashboard work for your specific trading style and preferences.
            </p>

            <div className="space-y-8">
              {customizationOptions.map((option, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-xl text-gray-900">{option.title}</CardTitle>
                    <p className="text-gray-600">{option.description}</p>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {option.options.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-start">
                          <Settings className="h-5 w-5 text-blue-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Best Practices */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard Best Practices</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-4 text-green-700">Do's</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Check market status before making trading decisions</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Regularly review and update your watchlists</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Set up alerts for key price levels and events</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Customize the layout to match your workflow</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-4 text-red-700">Don'ts</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't ignore market status indicators</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't overwhelm your dashboard with too many widgets</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't forget to act on important alerts promptly</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't rely solely on dashboard data for major decisions</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Ready for the Next Step?</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">Setting Up Your First Stock Screener</h3>
                  <p className="text-gray-600 mb-4">
                    Now that you understand the dashboard, learn how to create powerful stock screeners to find trading opportunities.
                  </p>
                  <Button asChild>
                    <Link to="/docs/getting-started/first-screener">
                      Create Your First Screener
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">How to Read Stock Data</h3>
                  <p className="text-gray-600 mb-4">
                    Learn to interpret the technical and fundamental data displayed throughout the platform.
                  </p>
                  <Button asChild variant="outline">
                    <Link to="/docs/getting-started/read-data">
                      Learn Data Interpretation
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;