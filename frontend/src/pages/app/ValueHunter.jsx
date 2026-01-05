import React, { useMemo, useRef, useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Alert, AlertDescription } from "../../components/ui/alert";
import * as htmlToImage from "html-to-image";
import { QRCodeCanvas } from "qrcode.react";
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Calendar,
  DollarSign,
  Activity,
  BarChart3,
  LineChart,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Loader2,
  Trophy,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  History,
  Zap,
  Share2,
  Twitter,
  Copy,
  Download
} from "lucide-react";
import { toast } from "sonner";
import { 
  getValueHunterCurrentWeek,
  getValueHunterWeek,
  listValueHunterWeeks,
  getValueHunterTopStocks
} from "../../api/client";
import { 
  LineChart as RechartsLineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";
import SEO from "../../components/SEO";
import logger from '../../lib/logger';
import { trackEvent as trackAnalyticsEvent, matomoTrackEvent } from "../../lib/analytics";

// Metric Card Component
const MetricCard = ({ title, value, subtitle, icon: Icon, trend, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-600 border-blue-200",
    green: "bg-green-50 text-green-600 border-green-200",
    red: "bg-red-50 text-red-600 border-red-200",
    yellow: "bg-yellow-50 text-yellow-600 border-yellow-200",
    purple: "bg-purple-50 text-purple-600 border-purple-200",
  };

  return (
    <Card className={`${colorClasses[color]} border`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium opacity-80">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && <p className="text-xs opacity-60">{subtitle}</p>}
          </div>
          <div className="p-3 rounded-full bg-white/50">
            <Icon className="h-6 w-6" />
          </div>
        </div>
        {trend !== undefined && (
          <div className="mt-2 flex items-center text-sm">
            {trend >= 0 ? (
              <ArrowUpRight className="h-4 w-4 mr-1 text-green-500" />
            ) : (
              <ArrowDownRight className="h-4 w-4 mr-1 text-red-500" />
            )}
            <span className={trend >= 0 ? "text-green-600" : "text-red-600"}>
              {trend >= 0 ? "+" : ""}{trend.toFixed(2)}%
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Stock Card Component for Top 10
const StockCard = ({ stock, rank }) => {
  const isPositive = stock.valuation_score >= 70;
  
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold text-sm">
              {rank}
            </div>
            <div>
              <h4 className="font-bold text-lg">{stock.symbol}</h4>
              <p className="text-sm text-gray-500">{stock.name || "Company Name"}</p>
            </div>
          </div>
          <Badge className={isPositive ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}>
            Score: {stock.valuation_score?.toFixed(1) || "N/A"}
          </Badge>
        </div>
        
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-500">Current Price</p>
            <p className="font-semibold">${stock.current_price?.toFixed(2) || "N/A"}</p>
          </div>
          <div>
            <p className="text-gray-500">Target Value</p>
            <p className="font-semibold text-green-600">${stock.target_value?.toFixed(2) || "N/A"}</p>
          </div>
          <div>
            <p className="text-gray-500">Upside</p>
            <p className="font-semibold text-blue-600">
              {stock.upside_potential ? `+${stock.upside_potential.toFixed(1)}%` : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Rating</p>
            <p className="font-semibold">{stock.valuation_status || "N/A"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Week Performance Card
const WeekPerformanceCard = ({ week, onView }) => {
  const isPositive = week.weekly_return >= 0;
  const alphaPositive = week.alpha >= 0;

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => onView(week)}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h4 className="font-semibold">Week {week.week_number}, {week.year}</h4>
            <p className="text-xs text-gray-500">
              {week.week_start} to {week.week_end}
            </p>
          </div>
          <Badge className={week.status === "completed" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}>
            {week.status}
          </Badge>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-gray-500">Weekly Return</p>
            <p className={`text-lg font-bold ${isPositive ? "text-green-600" : "text-red-600"}`}>
              {isPositive ? "+" : ""}{week.weekly_return?.toFixed(2) || 0}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Alpha vs Market</p>
            <p className={`text-lg font-bold ${alphaPositive ? "text-green-600" : "text-red-600"}`}>
              {alphaPositive ? "+" : ""}{week.alpha?.toFixed(2) || 0}%
            </p>
          </div>
        </div>
        
        {week.cumulative_return !== undefined && (
          <div className="mt-3 pt-3 border-t">
            <p className="text-xs text-gray-500">Cumulative Return</p>
            <p className="text-sm font-semibold text-blue-600">
              {week.cumulative_return >= 0 ? "+" : ""}{week.cumulative_return?.toFixed(2)}%
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default function ValueHunter() {
  const [activeTab, setActiveTab] = useState("current");
  const [currentWeek, setCurrentWeek] = useState(null);
  const [selectedWeek, setSelectedWeek] = useState(null);
  const [weekHistory, setWeekHistory] = useState([]);
  const [topStocks, setTopStocks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [topStocksLoading, setTopStocksLoading] = useState(false);
  const [shareExporting, setShareExporting] = useState(false);

  const shareCardRef = useRef(null);

  // Load current week on mount
  useEffect(() => {
    loadCurrentWeek();
    loadTopStocks();
  }, []);

  // Load history when switching to history tab
  useEffect(() => {
    if (activeTab === "history") {
      loadWeekHistory();
    }
  }, [activeTab]);

  const loadCurrentWeek = async () => {
    setIsLoading(true);
    try {
      const response = await getValueHunterCurrentWeek();
      if (response.success) {
        setCurrentWeek(response.week);
      } else {
        logger.info("No current week active");
      }
    } catch (error) {
      logger.error("Failed to load current week:", error);
      toast.error("Failed to load current week data");
    } finally {
      setIsLoading(false);
    }
  };

  const loadWeekHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await listValueHunterWeeks();
      if (response.success) {
        setWeekHistory(response.weeks || []);
      }
    } catch (error) {
      logger.error("Failed to load week history:", error);
      toast.error("Failed to load history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const loadTopStocks = async () => {
    setTopStocksLoading(true);
    try {
      const response = await getValueHunterTopStocks();
      if (response.success) {
        setTopStocks(response.stocks || []);
      }
    } catch (error) {
      logger.error("Failed to load top stocks:", error);
    } finally {
      setTopStocksLoading(false);
    }
  };

  const handleViewWeek = (week) => {
    setSelectedWeek(week);
    setActiveTab("current");
  };

  const displayWeek = selectedWeek || currentWeek;

  const shareText = useMemo(() => {
    const weekLabel = displayWeek ? `Week ${displayWeek.week_number}, ${displayWeek.year}` : "this week";
    const picks = (topStocks || []).slice(0, 5).map((s) => s.symbol).filter(Boolean).join(", ");
    return `My Value Hunter picks for ${weekLabel} on @TradeScanPro 🏆

Top picks: ${picks || "loading..."}
Try it 👉 ${window.location.origin}`;
  }, [displayWeek, topStocks]);

  const copyShareText = async () => {
    try {
      await navigator.clipboard.writeText(shareText);
      toast.success("Share text copied!");
      trackAnalyticsEvent("value_hunter_share_text_copied", { week: displayWeek?.week_number, year: displayWeek?.year });
      matomoTrackEvent("ValueHunter", "Share", "copy_text", 1);
    } catch {
      toast.error("Failed to copy");
    }
  };

  const shareToTwitter = () => {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`, "_blank", "width=550,height=420");
    trackAnalyticsEvent("value_hunter_shared", { platform: "twitter", week: displayWeek?.week_number, year: displayWeek?.year });
    matomoTrackEvent("ValueHunter", "Share", "twitter", 1);
  };

  const exportWeeklyPicksPNG = async () => {
    if (!shareCardRef.current) return;
    if (!topStocks || topStocks.length === 0) {
      toast.error("No picks to export yet");
      return;
    }
    setShareExporting(true);
    try {
      const dataUrl = await htmlToImage.toPng(shareCardRef.current, {
        quality: 0.98,
        pixelRatio: 2,
        backgroundColor: "#ffffff",
        width: 1200,
        height: 628,
        style: { width: "1200px", height: "628px" },
      });
      const link = document.createElement("a");
      const y = displayWeek?.year || new Date().getFullYear();
      const w = displayWeek?.week_number || "current";
      link.download = `value-hunter-picks-${y}-w${w}.png`;
      link.href = dataUrl;
      link.click();
      toast.success("Image exported!");
      trackAnalyticsEvent("value_hunter_image_exported", { week: displayWeek?.week_number, year: displayWeek?.year });
      matomoTrackEvent("ValueHunter", "Export", "png", 1);
    } catch {
      toast.error("Failed to export image");
    } finally {
      setShareExporting(false);
    }
  };

  // Prepare performance chart data
  const performanceData = weekHistory.slice(0, 10).reverse().map((week) => ({
    week: `W${week.week_number}`,
    return: week.weekly_return || 0,
    benchmark: week.benchmark_return || 0,
    alpha: week.alpha || 0
  }));

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl" data-testid="value-hunter-page">
      <SEO 
        title="Value Hunter Portfolio | Trade Scan Pro" 
        description="Automated weekly portfolio of top undervalued stocks"
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Value Hunter Portfolio</h1>
            <p className="text-gray-500">Automated weekly portfolio of top 10 undervalued stocks</p>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-3">
          <Badge variant="outline" className="bg-green-50">
            <CheckCircle className="h-3 w-3 mr-1 text-green-600" />
            Algorithmic Selection
          </Badge>
          <Badge variant="outline" className="bg-blue-50">
            <Calendar className="h-3 w-3 mr-1 text-blue-600" />
            Monday Entry / Friday Exit
          </Badge>
        </div>

        {/* Offscreen share card */}
        <div className="fixed left-[-10000px] top-0" aria-hidden="true">
          <div ref={shareCardRef} style={{ width: 1200, height: 628 }} className="bg-white border border-gray-200 overflow-hidden">
            <div className="h-full w-full flex flex-col">
              <div className="px-10 pt-8 pb-6 bg-gradient-to-r from-green-600 to-blue-600 text-white">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-sm font-semibold opacity-90">TradeScanPro</div>
                    <div className="text-4xl font-bold mt-1">Value Hunter Picks</div>
                    <div className="text-lg opacity-90 mt-2">
                      {displayWeek ? `Week ${displayWeek.week_number}, ${displayWeek.year}` : "This week"}
                    </div>
                  </div>
                  <div className="bg-white rounded-xl p-3 shadow-sm">
                    <QRCodeCanvas value={`${window.location.origin}/app/value-hunter`} size={120} includeMargin />
                  </div>
                </div>
              </div>
              <div className="flex-1 px-10 py-8">
                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-xl border border-gray-200 p-4">
                    <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Top 10 tickers</div>
                    <div className="mt-3 grid grid-cols-5 gap-2">
                      {(topStocks || []).slice(0, 10).map((s, i) => (
                        <div key={`${s.symbol}-${i}`} className="rounded-lg border bg-gray-50 p-2 text-center">
                          <div className="text-xs text-gray-500">#{i + 1}</div>
                          <div className="text-sm font-bold text-gray-900">{s.symbol}</div>
                          <div className="text-[10px] text-blue-600">Score {Number(s.valuation_score || 0).toFixed(0)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-xl border border-gray-200 p-4">
                    <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Why these picks</div>
                    <div className="mt-3 text-sm text-gray-700">
                      Screened for undervaluation and quality signals. Always validate with your own risk management.
                    </div>
                    <div className="mt-6 rounded-lg bg-gray-50 border border-gray-200 p-3 text-xs text-gray-600 whitespace-pre-line font-mono">
                      {shareText}
                    </div>
                  </div>
                </div>
              </div>
              <div className="px-10 py-5 border-t border-gray-200 flex items-center justify-between">
                <div className="text-sm text-gray-600">Weekly picks • Track record • Alpha</div>
                <div className="text-sm font-semibold text-gray-900">TradeScanPro.com</div>
              </div>
            </div>
          </div>
        </div>

        {/* Sharing actions */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <Button variant="outline" onClick={shareToTwitter}>
            <Twitter className="h-4 w-4 mr-2 text-blue-500" />
            Share
          </Button>
          <Button variant="outline" onClick={copyShareText}>
            <Copy className="h-4 w-4 mr-2" />
            Copy text
          </Button>
          <Button variant="outline" onClick={exportWeeklyPicksPNG} disabled={shareExporting}>
            {shareExporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
            Export PNG
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
          <TabsTrigger value="current" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Current Week
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-2">
            <Star className="h-4 w-4" />
            Top 10 Stocks
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Current Week Tab */}
        <TabsContent value="current" className="space-y-6">
          {isLoading ? (
            <Card className="p-12 text-center">
              <Loader2 className="h-12 w-12 mx-auto text-blue-500 animate-spin mb-4" />
              <p className="text-gray-500">Loading portfolio data...</p>
            </Card>
          ) : displayWeek ? (
            <>
              {/* Week Overview */}
              <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-0">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold">
                        Week {displayWeek.week_number}, {displayWeek.year}
                      </h2>
                      <p className="text-gray-600">
                        {displayWeek.week_start} to {displayWeek.week_end}
                      </p>
                      <Badge className="mt-2" variant="outline">
                        <Clock className="h-3 w-3 mr-1" />
                        {displayWeek.status}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold">
                        <span className={displayWeek.weekly_return >= 0 ? "text-green-600" : "text-red-600"}>
                          {displayWeek.weekly_return >= 0 ? "+" : ""}
                          {displayWeek.weekly_return?.toFixed(2) || 0}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">Weekly Return</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard
                  title="Starting Capital"
                  value={`$${(displayWeek.starting_capital || 0).toLocaleString()}`}
                  icon={DollarSign}
                  color="blue"
                />
                <MetricCard
                  title="Ending Capital"
                  value={`$${(displayWeek.ending_capital || 0).toLocaleString()}`}
                  icon={TrendingUp}
                  color={displayWeek.ending_capital >= displayWeek.starting_capital ? "green" : "red"}
                />
                <MetricCard
                  title="Alpha vs Market"
                  value={`${displayWeek.alpha >= 0 ? "+" : ""}${displayWeek.alpha?.toFixed(2) || 0}%`}
                  subtitle="Outperformance"
                  icon={Zap}
                  color={displayWeek.alpha >= 0 ? "green" : "red"}
                />
                <MetricCard
                  title="Cumulative Return"
                  value={`${displayWeek.cumulative_return >= 0 ? "+" : ""}${displayWeek.cumulative_return?.toFixed(2) || 0}%`}
                  subtitle="Year to date"
                  icon={Trophy}
                  color="purple"
                />
              </div>

              {/* Positions Table */}
              {displayWeek.positions && displayWeek.positions.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Portfolio Positions</CardTitle>
                    <CardDescription>
                      {displayWeek.positions.length} stocks selected by valuation algorithm
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-3 px-3 font-medium text-gray-500">Symbol</th>
                            <th className="text-right py-3 px-3 font-medium text-gray-500">Shares</th>
                            <th className="text-right py-3 px-3 font-medium text-gray-500">Entry Price</th>
                            <th className="text-right py-3 px-3 font-medium text-gray-500">Exit Price</th>
                            <th className="text-right py-3 px-3 font-medium text-gray-500">Return</th>
                          </tr>
                        </thead>
                        <tbody>
                          {displayWeek.positions.map((position, index) => (
                            <tr key={index} className="border-b hover:bg-gray-50">
                              <td className="py-3 px-3">
                                <span className="font-semibold">{position.symbol}</span>
                              </td>
                              <td className="py-3 px-3 text-right">
                                {position.shares?.toFixed(2) || "N/A"}
                              </td>
                              <td className="py-3 px-3 text-right">
                                ${position.entry_price?.toFixed(2) || "N/A"}
                              </td>
                              <td className="py-3 px-3 text-right">
                                {position.exit_price ? `$${position.exit_price.toFixed(2)}` : "-"}
                              </td>
                              <td className={`py-3 px-3 text-right font-semibold ${
                                position.return_percent >= 0 ? "text-green-600" : "text-red-600"
                              }`}>
                                {position.return_percent !== null 
                                  ? `${position.return_percent >= 0 ? "+" : ""}${position.return_percent.toFixed(2)}%`
                                  : "-"}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Strategy Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-blue-500" />
                    How It Works
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Target className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm">Algorithmic Selection</h4>
                      <p className="text-sm text-gray-600">
                        Top 10 most undervalued stocks based on our composite valuation score
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Calendar className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm">Weekly Rebalancing</h4>
                      <p className="text-sm text-gray-600">
                        Entry every Monday at 9:35 AM ET, exit every Friday at 3:55 PM ET
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <BarChart3 className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm">Value-Focused</h4>
                      <p className="text-sm text-gray-600">
                        Uses DCF, EPV, Graham Number, and other fundamental metrics
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="p-12 text-center">
              <Activity className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No Active Week</h3>
              <p className="text-gray-500 mt-1">
                The portfolio is currently inactive. Check back on Monday for the new week's selections.
              </p>
            </Card>
          )}
        </TabsContent>

        {/* Top 10 Stocks Preview Tab */}
        <TabsContent value="preview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                Top 10 Undervalued Stocks
              </CardTitle>
              <CardDescription>
                Current candidates for next week's portfolio based on valuation scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              {topStocksLoading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                </div>
              ) : topStocks.length > 0 ? (
                <div className="grid md:grid-cols-2 gap-4">
                  {topStocks.map((stock, index) => (
                    <StockCard key={stock.symbol} stock={stock} rank={index + 1} />
                  ))}
                </div>
              ) : (
                <div className="text-center p-8">
                  <Star className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">No Stocks Available</h3>
                  <p className="text-gray-500 mt-1">Top stocks data is currently unavailable</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6">
          {/* Performance Chart */}
          {performanceData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5 text-blue-500" />
                  Weekly Performance
                </CardTitle>
                <CardDescription>Last 10 weeks performance vs market benchmark</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsLineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis 
                        dataKey="week" 
                        stroke="#9CA3AF"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis 
                        stroke="#9CA3AF"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => `${value.toFixed(0)}%`}
                      />
                      <Tooltip 
                        formatter={(value) => `${value.toFixed(2)}%`}
                        contentStyle={{ borderRadius: 8, border: "1px solid #E5E7EB" }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="return" 
                        stroke="#10B981" 
                        strokeWidth={2}
                        name="Portfolio Return"
                        dot={{ fill: "#10B981" }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="benchmark" 
                        stroke="#6B7280" 
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        name="Benchmark"
                        dot={{ fill: "#6B7280" }}
                      />
                    </RechartsLineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}

          {/* History List */}
          <Card>
            <CardHeader>
              <CardTitle>Portfolio History</CardTitle>
              <CardDescription>Past weekly portfolio results</CardDescription>
            </CardHeader>
            <CardContent>
              {historyLoading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
              ) : weekHistory.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {weekHistory.map((week) => (
                    <WeekPerformanceCard
                      key={`${week.year}-${week.week_number}`}
                      week={week}
                      onView={handleViewWeek}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center p-8">
                  <History className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">No History Yet</h3>
                  <p className="text-gray-500 mt-1">Portfolio history will appear here after weeks are completed</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Disclaimer */}
      <Alert className="mt-6 bg-yellow-50 border-yellow-200">
        <AlertCircle className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-700">
          <strong>Disclaimer:</strong> Past performance does not guarantee future results. 
          This is an algorithmic portfolio based on fundamental analysis and should not be considered as investment advice.
        </AlertDescription>
      </Alert>
    </div>
  );
}
