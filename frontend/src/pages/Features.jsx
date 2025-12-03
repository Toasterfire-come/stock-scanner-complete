import React, { useState, useEffect } from "react";
import SEO from "../components/SEO";
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
  ArrowRight,
  LineChart,
  Download,
  Sliders,
  Table2,
  Gauge
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import {
  marketingMetrics,
  formatNumber,
  formatPercent,
  timeframeCopy,
} from "../data/marketingMetrics";

const Features = () => {
  const [platformStats, setPlatformStats] = useState(null);
  const { usage, outcomes, reliability, enterprise } = marketingMetrics;

  useEffect(() => {
    const fetchPlatformStats = async () => {
      try {
        const { data } = await api.get('/status/');
        setPlatformStats(data);
      } catch (error) {
        console.error("Failed to fetch platform stats:", error);
      }
    };

    fetchPlatformStats();
  }, []);

  const mainFeatures = [
    {
      icon: <LineChart className="h-8 w-8" />,
      title: "Advanced Charting & Technical Analysis",
      description: "Professional-grade charting with 9 timeframes and 8 technical indicators for all trading styles.",
      details: [
        "9 Timeframes: 1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W, 1M (Premium: 1m, 5m, 4H)",
        "8 Technical Indicators: SMA, EMA, RSI, MACD, Bollinger Bands, VWAP, Stochastic, ATR",
        "4 chart types: Candlestick, Line, Area, Heikin-Ashi (Premium)",
        "Drawing tools and indicator overlays",
        "Export to PNG, SVG, or CSV with high DPI support",
        `${reliability.apiP50LatencyMs}ms P50 latency for smooth real-time charting`
      ],
      highlight: true
    },
    {
      icon: <Search className="h-8 w-8" />,
      title: "Real-Time Screeners & Scanners",
      description: `Screen ${formatNumber(usage.coverageUniverse)}+ equities with momentum, breakout, and value filters for all trading styles.`,
      details: [
        `Complete coverage across ${usage.coverageVenues.join(", ")} (${formatNumber(usage.coverageUniverse)}+ tickers)`,
        "Day Trading: Momentum scanners, gap plays, breakout screeners, volume alerts",
        "Swing Trading: Technical patterns, 20/50 EMA crossovers, RSI setups",
        "Long-Term: Fundamental filters (P/E, ROE, debt ratios), dividend screening",
        `${formatNumber(usage.totalScreenersRunMonthly)}+ screeners run monthly`,
        "Save presets and share screeners across teams"
      ],
      highlight: true
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: "Value Hunter - Fair Value Analysis",
      description: "Automated weekly portfolio that identifies undervalued stocks using professional DCF models.",
      details: [
        "Discounted Cash Flow (DCF) valuation for any stock",
        "Earnings Power Value (EPV) and Graham Number calculations",
        "Margin of Safety scoring - know how much discount you're getting",
        "Automated weekly portfolio selection (top 10 undervalued stocks)",
        "Historical performance tracking and backtested results",
        "Portfolio-wide fair value analysis"
      ]
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "AI-Powered Strategy Backtesting",
      description: "Test ANY trading strategy - day trading, swing trading, or long-term - with AI-enhanced insights.",
      details: [
        "Backtest any strategy with 5+ years of historical data",
        "AI explains WHY your strategy works (or doesn't)",
        "20 baseline strategies: 7 day trading, 7 swing, 6 long-term",
        "Risk-adjusted return metrics (Sharpe, Sortino, Max Drawdown)",
        "Compare multiple strategies side-by-side",
        "Export detailed backtest reports (Premium: 5 backtests/month)"
      ]
    },
    {
      icon: <Bell className="h-8 w-8" />,
      title: "Smart Alerts & Notifications",
      description: "Near real-time alerts for price movements, technical signals, and fundamental changes.",
      details: [
        `Price movement alerts with sub-${reliability.apiP95LatencyMs}ms delivery`,
        "Technical alerts: RSI overbought/oversold, MACD crossovers, breakout signals",
        "Fair value threshold alerts - know when stocks become undervalued",
        "Fundamental changes (earnings surprises, dividend announcements)",
        `${formatNumber(usage.alertsDeliveredMonthly)}+ alerts delivered monthly`,
        "Email and push notification delivery"
      ]
    },
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Portfolio & Journal",
      description: "Track performance with professional analytics, trading journal, and tax reporting.",
      details: [
        "Portfolio valuation with intraday P&L tracking",
        "Trading Journal: Record all trades with notes, screenshots, emotions",
        "Tax Reporting: Automated cost basis tracking and tax lot management",
        `Performance analytics with ${formatPercent(outcomes.averageDrawdownReductionPercent)} avg drawdown reduction`,
        `Diversification insights across ${formatNumber(usage.watchlistsSyncedMonthly)} synced watchlists`,
        "Historical performance charts and metrics"
      ]
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Fundamental Analysis & Insider Trading",
      description: "50+ fundamental metrics, DCF valuations, and SEC insider transaction tracking.",
      details: [
        "50+ fundamental metrics: P/E, ROE, debt ratios, margins, growth rates",
        "SEC insider transactions by executives and directors",
        "Aggregate insider sentiment by ticker",
        "Fair value estimates vs current price",
        `Insights backed by ${marketingMetrics.testimonials.verifiedCaseStudies}+ verified case studies`,
        "Daily updates for all fundamental data"
      ]
    }
  ];

  const additionalFeatures = [
    {
      icon: <Target className="h-6 w-6" />,
      title: "Watchlists",
      description: "Organize favorites, bulk add/remove, and share read‑only links"
    },
    {
      icon: <Eye className="h-6 w-6" />,
      title: "Market Overview",
      description: "Heatmaps, sector trends, top gainers/losers, and most active"
    },
    {
      icon: <Cloud className="h-6 w-6" />,
      title: "Cloud Sync",
      description: "Securely sync portfolios, alerts, and screeners across devices"
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Security",
      description: "CSRF protection, session management, and privacy‑first analytics"
    },
    {
      icon: <Bell className="h-6 w-6" />,
      title: "Alerts",
      description: "Price, % change, volume spike, and indicator crossovers"
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Exports",
      description: "Export screener and portfolio data to CSV in one click"
    },
    {
      icon: <Table2 className="h-6 w-6" />,
      title: "Enhanced Data Tables",
      description: "Virtual scrolling for 10k+ rows with advanced sorting and filtering"
    },
    {
      icon: <Download className="h-6 w-6" />,
      title: "Multi-Format Export",
      description: "Export charts as PNG, SVG, or CSV with high DPI support"
    },
    {
      icon: <Sliders className="h-6 w-6" />,
      title: "Indicator Customization",
      description: "Full control over technical indicators with period, color, and line width settings"
    },
    {
      icon: <Gauge className="h-6 w-6" />,
      title: "Real-Time Performance",
      description: `${reliability.dataFreshnessSeconds}s data freshness with ${reliability.apiP50LatencyMs}ms P50 API latency`
    }
  ];

  const proModules = [
    {
      icon: <LineChart className="h-6 w-6" />,
      title: "Professional Charting Suite",
      points: [
        "4 chart types: candlestick, line, area, bar",
        "4 professional themes for any lighting",
        "Export to PNG (high DPI), SVG (vector), CSV",
        "Fullscreen mode with gesture controls",
        "Custom indicator overlays and settings"
      ]
    },
    {
      icon: <Table2 className="h-6 w-6" />,
      title: "Advanced Data Management",
      points: [
        "Virtual scrolling handles 10,000+ rows seamlessly",
        "Column sorting with multi-level support",
        "Global search and per-column filtering",
        "Row selection (single/multi) with bulk actions",
        "Sticky headers for easy navigation",
        "Loading states and empty state messaging"
      ]
    },
    {
      icon: <Sliders className="h-6 w-6" />,
      title: "Enhanced UI Components",
      points: [
        "Select components with search and grouping",
        "Virtual scrolling for large option lists",
        "Icons and badges support in dropdowns",
        "Custom scrollbar styling",
        "Mobile-responsive compact modes",
        "Keyboard navigation support"
      ]
    }
  ];

  const metricHighlights = [
    {
      label: "Screeners run monthly",
      value: `${formatNumber(usage.totalScreenersRunMonthly)}+`,
    },
    {
      label: "Trial-to-paid conversion",
      value: formatPercent(outcomes.trialToPaidConversionPercent),
    },
    {
      label: "90-day retention",
      value: formatPercent(marketingMetrics.testimonials.retentionPercent90Day),
    },
    {
      label: "Platform uptime",
      value: formatPercent(reliability.uptimePercent, 2),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="Features | Value Investing Tools & Fundamental Analysis"
        description="Powerful stock filter and market scan: build filters by price, volume, RSI, insider buys; run real-time scans with alerts and watchlists."
        url="https://tradescanpro.com/features"
        jsonLdUrls={["/structured/features.jsonld"]}
      />
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Zap className="h-4 w-4 mr-2" />
              Feature telemetry from {timeframeCopy()}
            </Badge>

            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Powerful Features for
              <span className="text-blue-600 block">Long-Term Investors</span>
            </h1>

            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              Build wealth with professional-grade fundamental analysis, AI-powered backtesting,
              and comprehensive educational resources trusted by {formatNumber(usage.activeAccounts)} investors.
            </p>

            <Button asChild size="lg" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Try Now for Free
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>

            <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              {metricHighlights.map((item) => (
                <div key={item.label} className="bg-white/80 border rounded-xl py-5 px-6 shadow-sm">
                  <div className="text-3xl font-bold text-blue-600 mb-2">{item.value}</div>
                  <div className="text-sm uppercase tracking-wide text-gray-600">{item.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Core Investment Tools
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built for value investors. Every feature helps you make smarter, data-driven investment decisions.
            </p>
          </div>
          
          <div className="space-y-16">
            {mainFeatures.map((feature, index) => (
              <div key={index} className={`flex flex-col lg:flex-row items-center gap-12 ${index % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
                <div className="lg:w-1/2">
                  <Card className={`hover:shadow-2xl transition-shadow duration-300 ${feature.highlight ? 'border-2 border-blue-500 bg-blue-50/30' : ''}`}>
                    <CardHeader>
                      <div className="flex items-center space-x-4 mb-4">
                        <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${feature.highlight ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-600'}`}>
                          {feature.icon}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-3xl">{feature.title}</CardTitle>
                            {feature.highlight && <Badge className="bg-blue-600">Featured</Badge>}
                          </div>
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
                  <div className="rounded-2xl overflow-hidden border bg-black">
                    <video
                      className="w-full h-64"
                      autoPlay
                      muted
                      loop
                      playsInline
                      preload="metadata"
                      poster={`/react/demos/${feature.title.toLowerCase().replace(/[^a-z0-9]+/g,'-')}.jpg`}
                    >
                      <source src={`/react/demos/${feature.title.toLowerCase().replace(/[^a-z0-9]+/g,'-')}.mp4`} type="video/mp4" />
                    </video>
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

      {/* Pro Modules */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Pro Modules
            </h2>
            <p className="text-xl text-gray-600">
              Unlock advanced capabilities with our professional toolset
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {proModules.map((mod, i) => (
              <Card key={i} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                      {mod.icon}
                    </div>
                    <CardTitle>{mod.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-2 text-gray-700">
                    {mod.points.map((p, idx) => (
                      <li key={idx}>{p}</li>
                    ))}
                  </ul>
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
                  All data is encrypted end-to-end with 12 consecutive compliance audits passed.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Clock className="h-16 w-16 text-green-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Reliable Service</h3>
                <p className="text-gray-600">
                  {formatPercent(reliability.uptimePercent, 2)} uptime with {reliability.incidentFreeDaysRolling} incident-free days and auto failover.
                </p>
              </CardContent>
            </Card>
            
            <Card className="text-center">
              <CardContent className="p-8">
                <Cloud className="h-16 w-16 text-purple-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold mb-4">Real-Time Data</h3>
                <p className="text-gray-600">
                  Access current market information with {reliability.apiP50LatencyMs}ms median API latency and {formatNumber(usage.watchlistsSyncedMonthly)} synced watchlists.
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
            Trials convert at {formatPercent(outcomes.trialToPaidConversionPercent)} when teams activate alerts and screeners in the first week. Give it a spin free until the next 1st.
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