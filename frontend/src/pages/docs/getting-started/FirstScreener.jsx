import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Alert, AlertDescription } from "../../../components/ui/alert";
import { 
  ArrowLeft,
  ArrowRight,
  Search,
  Filter,
  TrendingUp,
  BarChart3,
  Clock,
  CheckCircle,
  Lightbulb,
  Play,
  Settings,
  Save
} from "lucide-react";
import { Link } from "react-router-dom";

const FirstScreener = () => {
  const screenerSteps = [
    {
      number: "01",
      title: "Access the Screener",
      description: "Navigate to the stock screener from your dashboard",
      details: [
        "Log into your Trade Scan Pro account",
        "Click 'Screeners' in the main navigation menu",
        "Select 'Create New Screener' or use the quick action button",
        "Choose 'Custom Screener' to build from scratch"
      ],
      tip: "You can also access the screener directly from the dashboard quick actions panel."
    },
    {
      number: "02",
      title: "Choose Your Criteria",
      description: "Select the technical and fundamental filters that match your strategy",
      details: [
        "Start with basic filters: Market Cap, Price Range, Volume",
        "Add technical indicators: RSI, MACD, Moving Averages",
        "Include fundamental metrics: P/E Ratio, EPS Growth, Revenue Growth",
        "Set logical operators (AND/OR) between filter groups"
      ],
      tip: "Start with 3-5 filters for your first screener. You can always add more complexity later."
    },
    {
      number: "03",
      title: "Set Filter Values",
      description: "Define the specific ranges and values for each filter",
      details: [
        "Market Cap: Choose from Micro ($50M-$300M), Small ($300M-$2B), Mid ($2B-$10B), Large ($10B+)",
        "Price Range: Set minimum and maximum stock prices (e.g., $5-$100)",
        "Volume: Set minimum daily volume (e.g., 500,000+ shares)",
        "RSI: Common ranges - Oversold (20-30), Neutral (30-70), Overbought (70-80)"
      ],
      tip: "Use broader ranges initially, then narrow them down as you see the results."
    },
    {
      number: "04",
      title: "Run Your Screen",
      description: "Execute the screener and review the results",
      details: [
        "Click 'Run Screener' to execute your filters",
        "Review the list of stocks that match your criteria",
        "Check the total number of results (aim for 20-50 stocks)",
        "Sort results by different metrics to find the best opportunities"
      ],
      tip: "If you get too many results (500+), add more restrictive filters. If too few (under 10), loosen some criteria."
    },
    {
      number: "05",
      title: "Analyze and Save",
      description: "Review the results and save your screener for future use",
      details: [
        "Click on individual stocks to view detailed information",
        "Add promising stocks to your watchlist",
        "Save the screener with a descriptive name (e.g., 'Small Cap Growth Stocks')",
        "Set up alerts to run this screener automatically"
      ],
      tip: "Name your screeners descriptively so you can easily find them later. Include the strategy or criteria in the name."
    }
  ];

  const commonStrategies = [
    {
      name: "Growth Stocks",
      description: "Companies with strong earnings and revenue growth",
      filters: [
        "Market Cap: > $1B",
        "EPS Growth: > 15%",
        "Revenue Growth: > 10%",
        "P/E Ratio: 15-40",
        "Price: > $10"
      ],
      useCase: "Long-term growth investors seeking companies with strong fundamentals"
    },
    {
      name: "Value Stocks",
      description: "Undervalued companies with strong fundamentals",
      filters: [
        "P/E Ratio: < 15",
        "P/B Ratio: < 2",
        "Debt to Equity: < 0.5",
        "Dividend Yield: > 2%",
        "Market Cap: > $500M"
      ],
      useCase: "Value investors looking for underpriced stocks with solid fundamentals"
    },
    {
      name: "Momentum Plays",
      description: "Stocks showing strong technical momentum",
      filters: [  
        "RSI: 50-70",
        "MACD: Bullish crossover",
        "Price above 50-day MA",
        "Volume: > 1M shares",
        "Price change (5d): > 5%"
      ],
      useCase: "Swing traders and momentum investors looking for trending stocks"
    },
    {
      name: "Dividend Stocks",
      description: "Reliable dividend-paying companies",
      filters: [
        "Dividend Yield: 3-8%",
        "Payout Ratio: < 70%",
        "Market Cap: > $2B",
        "P/E Ratio: < 20",
        "Debt to Equity: < 0.6"
      ],
      useCase: "Income investors seeking stable dividend payments"
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
                <Search className="h-4 w-4 mr-2" />
                Getting Started
              </Badge>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                Setting Up Your First Stock Screener
              </h1>
              <p className="text-xl text-gray-700 leading-relaxed">
                Learn how to create powerful stock screeners that find trading opportunities matching your specific criteria.
                This guide will walk you through building your first screener step-by-step.
              </p>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600 mb-8">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                7 min read
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                Updated Dec 2024
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="pb-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <Alert className="border-blue-200 bg-blue-50">
              <Play className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Ready to Start?</strong> If you already understand the basics, <Link to="/app/screeners/new" className="underline font-medium">jump directly to the screener tool</Link> and start building!
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>

      {/* Step by Step Guide */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-12">Step-by-Step Guide</h2>
            
            <div className="space-y-8">
              {screenerSteps.map((step, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                        {step.number}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl text-gray-900">{step.title}</CardTitle>
                        <p className="text-gray-600 mt-1">{step.description}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <ul className="space-y-3 mb-6">
                      {step.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{detail}</span>
                        </li>
                      ))}
                    </ul>
                    <Alert>
                      <Lightbulb className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Pro Tip:</strong> {step.tip}
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Common Strategies */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Popular Screener Strategies</h2>
              <p className="text-xl text-gray-600">
                Get started quickly with these proven screening strategies
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {commonStrategies.map((strategy, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl text-gray-900">{strategy.name}</CardTitle>
                      <Badge variant="outline" className="text-xs">
                        Template
                      </Badge>
                    </div>
                    <p className="text-gray-600">{strategy.description}</p>
                  </CardHeader>
                  <CardContent>
                    <h4 className="font-semibold text-gray-900 mb-3">Filter Criteria:</h4>
                    <ul className="space-y-2 mb-4">
                      {strategy.filters.map((filter, filterIndex) => (
                        <li key={filterIndex} className="flex items-center text-sm">
                          <Filter className="h-4 w-4 text-blue-500 mr-2 flex-shrink-0" />
                          {filter}
                        </li>
                      ))}
                    </ul>
                    <div className="bg-gray-50 p-3 rounded-lg mb-4">
                      <p className="text-sm text-gray-700">
                        <strong>Best for:</strong> {strategy.useCase}
                      </p>
                    </div>
                    <Button variant="outline" className="w-full">
                      <Play className="h-4 w-4 mr-2" />
                      Use This Template
                    </Button>
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
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Screener Best Practices</h2>
            
            <div className="grid md:grid-cols-2 gap-8 mb-12">
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-4 text-green-700">Do's</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Start with broad criteria and narrow down</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Save successful screeners for reuse</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Review and update criteria regularly</span>
                    </li>
                    <li className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>Test screeners in different market conditions</span>
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
                      <span>Don't use too many restrictive filters initially</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't ignore the total number of results</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't rely on a single screener for all decisions</span>
                    </li>
                    <li className="flex items-start">
                      <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        <span className="text-white text-xs">×</span>
                      </div>
                      <span>Don't forget to verify results with additional analysis</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>

            <Alert className="border-blue-200 bg-blue-50">
              <Settings className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Remember:</strong> Screeners are tools to identify potential opportunities, not buy/sell recommendations. 
                Always perform additional research before making investment decisions.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">What's Next?</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">Advanced Screening Techniques</h3>
                  <p className="text-gray-600 mb-4">
                    Learn to combine multiple indicators and create sophisticated screening strategies.
                  </p>
                  <Button asChild>
                    <Link to="/docs/stock-screening/advanced-techniques">
                      Learn Advanced Techniques
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-3">Understanding Technical Indicators</h3>
                  <p className="text-gray-600 mb-4">
                    Deep dive into RSI, MACD, Moving Averages and other technical analysis tools.
                  </p>
                  <Button asChild variant="outline">
                    <Link to="/docs/stock-screening/technical-indicators">
                      Master Technical Analysis
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Create Your First Screener?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Put your knowledge to practice and start finding great trading opportunities today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/app/screeners/new">
                <Search className="h-5 w-5 mr-2" />
                Create Your First Screener
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-700" asChild>
              <Link to="/docs/stock-screening">
                Browse More Guides
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FirstScreener;