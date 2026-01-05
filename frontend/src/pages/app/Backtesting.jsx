import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Textarea } from "../../components/ui/textarea";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Progress } from "../../components/ui/progress";
import { Checkbox } from "../../components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "../../components/ui/dialog";
import * as htmlToImage from 'html-to-image';
import { QRCodeCanvas } from "qrcode.react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import {
  Brain,
  Play,
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  DollarSign,
  BarChart3,
  LineChart,
  Trophy,
  AlertCircle,
  CheckCircle,
  Loader2,
  Sparkles,
  History,
  Zap,
  ChevronRight,
  Share2,
  Twitter,
  Linkedin,
  Share,
  Copy,
  Check,
  Download,
  Image,
  FileText,
  Code
} from "lucide-react";
import { toast } from "sonner";
import { 
  createBacktest, 
  runBacktest, 
  getBacktest, 
  listBacktests, 
  getBaselineStrategies,
  shareBacktest,
  revokeSharedBacktest
} from "../../api/client";
import { 
  LineChart as RechartsLineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart
} from "recharts";
import SEO from "../../components/SEO";
import logger from '../../lib/logger';
import { trackEvent as trackAnalyticsEvent, matomoTrackEvent } from "../../lib/analytics";
import AchievementUnlock from "../../components/AchievementUnlock";

// Baseline strategy templates
const BASELINE_STRATEGIES = {
  day_trading: [
    { id: 1, name: "Opening Range Breakout (ORB)", description: "Buy when price breaks above the first 15-minute high, sell at end of day or when price breaks below the opening range low." },
    { id: 2, name: "VWAP Bounce", description: "Buy when price pulls back to VWAP and bounces with increasing volume. Exit when price reaches 1% profit or falls 0.5% below entry." },
    { id: 3, name: "Gap and Go", description: "Buy stocks gapping up 3%+ at market open with high volume. Sell when momentum fades or at 2% profit target." },
    { id: 4, name: "Red to Green Move", description: "Buy when a stock goes from red to green for the day with volume confirmation. Exit at prior day high or 3% profit." },
    { id: 5, name: "9 EMA Scalping", description: "Buy when price crosses above 9 EMA on 5-min chart. Sell when price closes below 9 EMA." },
    { id: 6, name: "High of Day Breakout", description: "Buy when price breaks to new intraday high with volume. Sell at 1.5% profit or end of day." },
    { id: 7, name: "Support/Resistance Reversal", description: "Buy at key support levels when price shows rejection. Sell at nearest resistance or 2% profit." },
  ],
  swing_trading: [
    { id: 8, name: "20/50 EMA Crossover", description: "Buy when 20 EMA crosses above 50 EMA. Sell when 20 EMA crosses below 50 EMA." },
    { id: 9, name: "RSI Oversold Bounce", description: "Buy when RSI drops below 30 and then rises back above 30. Sell when RSI reaches 70 or after 5 days." },
    { id: 10, name: "Cup and Handle Pattern", description: "Buy on breakout above handle resistance with volume. Sell at measured move target or 10% stop loss." },
    { id: 11, name: "Bollinger Band Squeeze", description: "Buy when price breaks above upper band after a squeeze. Sell when price touches middle band or 8% profit." },
    { id: 12, name: "MACD Histogram Reversal", description: "Buy when MACD histogram turns positive after being negative. Sell when histogram turns negative again." },
    { id: 13, name: "Weekly Breakout", description: "Buy when price breaks above the prior week's high. Sell when price breaks below prior week's low." },
    { id: 14, name: "Mean Reversion to 50 SMA", description: "Buy when price is 10%+ below 50 SMA. Sell when price returns to 50 SMA." },
  ],
  long_term: [
    { id: 15, name: "Graham Value Investing", description: "Buy stocks with P/E below 15, P/B below 1.5, and debt-to-equity below 0.5. Hold for 1 year minimum." },
    { id: 16, name: "Dividend Growth Strategy", description: "Buy stocks with 10+ years of consecutive dividend increases and yield above 2%. Hold indefinitely." },
    { id: 17, name: "Growth at Reasonable Price (GARP)", description: "Buy stocks with PEG ratio below 1 and earnings growth above 15%. Hold until PEG exceeds 2." },
    { id: 18, name: "Dogs of the Dow", description: "Buy the 10 highest-yielding Dow stocks at year start. Rebalance annually." },
    { id: 19, name: "Momentum Factor Strategy", description: "Buy top 10% of stocks by 12-month momentum. Rebalance monthly." },
    { id: 20, name: "Small Cap Value", description: "Buy small cap stocks (market cap under $2B) with lowest P/E ratios. Hold for 1 year." },
  ],
};

const CATEGORY_LABELS = {
  day_trading: "Day Trading",
  swing_trading: "Swing Trading",
  long_term: "Long-Term"
};

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
              <TrendingUp className="h-4 w-4 mr-1 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 mr-1 text-red-500" />
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

// Strategy Card Component
const StrategyCard = ({ strategy, onSelect, selected }) => (
  <Card 
    className={`cursor-pointer transition-all hover:shadow-md ${
      selected ? "ring-2 ring-blue-500 bg-blue-50" : "hover:bg-gray-50"
    }`}
    onClick={() => onSelect(strategy)}
  >
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-semibold text-sm">{strategy.name}</h4>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{strategy.description}</p>
        </div>
        {selected && <CheckCircle className="h-5 w-5 text-blue-500 flex-shrink-0 ml-2" />}
      </div>
    </CardContent>
  </Card>
);

// Backtest History Item
const BacktestHistoryItem = ({ backtest, onView, selectedForCompare, onToggleCompare }) => {
  const statusColors = {
    completed: "bg-green-100 text-green-700",
    pending: "bg-yellow-100 text-yellow-700",
    processing: "bg-blue-100 text-blue-700",
    failed: "bg-red-100 text-red-700"
  };

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => onView(backtest)}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <button
            type="button"
            className="mt-1"
            onClick={(e) => {
              e.stopPropagation();
              onToggleCompare?.(backtest.id);
            }}
            aria-label="Select for comparison"
          >
            <Checkbox checked={!!selectedForCompare} />
          </button>
          <div>
            <h4 className="font-semibold">{backtest.name}</h4>
            <p className="text-sm text-gray-500">{CATEGORY_LABELS[backtest.category]}</p>
          </div>
          <div className="text-right">
            <Badge className={statusColors[backtest.status]}>{backtest.status}</Badge>
            {backtest.total_return !== null && (
              <p className={`text-lg font-bold mt-1 ${backtest.total_return >= 0 ? "text-green-600" : "text-red-600"}`}>
                {backtest.total_return >= 0 ? "+" : ""}{backtest.total_return?.toFixed(2)}%
              </p>
            )}
          </div>
        </div>
        {backtest.composite_score !== null && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Score</span>
              <span className="font-medium">{backtest.composite_score?.toFixed(1)}/100</span>
            </div>
            <Progress value={backtest.composite_score} className="h-2 mt-1" />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default function Backtesting() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("create");
  const [category, setCategory] = useState("swing_trading");
  const [strategyText, setStrategyText] = useState("");
  const [selectedBaseline, setSelectedBaseline] = useState(null);
  const [symbols, setSymbols] = useState("AAPL");
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setFullYear(d.getFullYear() - 1);
    return d.toISOString().split("T")[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [initialCapital, setInitialCapital] = useState("10000");
  const [backtestName, setBacktestName] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [currentBacktest, setCurrentBacktest] = useState(null);
  const [backtestHistory, setBacktestHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportPreset, setExportPreset] = useState("twitter");
  const [achievementQueue, setAchievementQueue] = useState([]);
  const [activeAchievement, setActiveAchievement] = useState(null);
  const [selectedCompareIds, setSelectedCompareIds] = useState([]);
  const [compareOpen, setCompareOpen] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareBacktests, setCompareBacktests] = useState([]);
  const [pdfExporting, setPdfExporting] = useState(false);
  const [embedOpen, setEmbedOpen] = useState(false);
  const [weeklyChallenge, setWeeklyChallenge] = useState(null);

  // Ref for export functionality
  const resultsCardRef = useRef(null);
  const exportCardRef = useRef(null);
  const exportShareUrlRef = useRef("");

  const EXPORT_PRESETS = {
    twitter: { id: "twitter", label: "Twitter/X (1200×628)", width: 1200, height: 628 },
    instagram_square: { id: "instagram_square", label: "Instagram (1080×1080)", width: 1080, height: 1080 },
  };

  const exportConfig = EXPORT_PRESETS[exportPreset] || EXPORT_PRESETS.twitter;

  // Share helper functions
  const getShareUrl = (backtest) => {
    const origin = window.location.origin;
    // Prefer stable slug URL when available
    if (backtest?.share_slug) return `${origin}/backtest/${backtest.share_slug}`;
    return `${origin}/share/backtest/${backtest.id}`;
  };

  const getShareUrlForExport = (backtest) => {
    if (!backtest) return "";
    if (backtest.share_slug) return getShareUrl(backtest);
    return exportShareUrlRef.current || getShareUrl(backtest);
  };

  const generateShareText = (backtest, shareUrlOverride) => {
    const { total_return, win_rate, sharpe_ratio, total_trades } = backtest.results || {};
    const emoji = total_return >= 50 ? "🚀" : total_return >= 20 ? "📈" : total_return >= 0 ? "✅" : "📉";
    const shareUrl = shareUrlOverride || getShareUrl(backtest);

    if (total_return >= 0) {
      return `I just backtested "${backtest.name}" on @TradeScanPro and got +${total_return?.toFixed(1)}% returns ${emoji}

Win rate: ${win_rate?.toFixed(1)}%
Sharpe: ${sharpe_ratio?.toFixed(2)}
Trades: ${total_trades}

Try it yourself 👉 ${shareUrl}`;
    } else {
      return `I tested "${backtest.name}" on @TradeScanPro ${emoji}

Return: ${total_return?.toFixed(1)}%
Win rate: ${win_rate?.toFixed(1)}%
Trades: ${total_trades}

Learn from my mistakes 👉 ${shareUrl}`;
    }
  };

  const ensurePublicShare = async (backtest) => {
    if (!backtest) return "";
    if (backtest.is_public && backtest.share_slug) return getShareUrl(backtest);

    try {
      const data = await shareBacktest(backtest.id);
      if (data?.success) {
        const slug = data.slug || data.share_slug;
        const shareUrl = data.share_url ? `${window.location.origin}${data.share_url}` : `${window.location.origin}/backtest/${slug}`;
        exportShareUrlRef.current = shareUrl;
        // Update local state to reflect public status + slug
        setCurrentBacktest((prev) => {
          if (!prev || prev.id !== backtest.id) return prev;
          return { ...prev, is_public: true, share_slug: slug };
        });
        return shareUrl;
      }
    } catch (e) {
      logger.warn("Failed to create share link", e);
    }

    return getShareUrl(backtest);
  };

  const setPrivateShare = async (backtest) => {
    if (!backtest) return;
    try {
      const data = await revokeSharedBacktest(backtest.id);
      if (data?.success) {
        setCurrentBacktest((prev) => {
          if (!prev || prev.id !== backtest.id) return prev;
          return { ...prev, is_public: false };
        });
        toast.success("Backtest is now private");
      } else {
        toast.error(data?.error || "Failed to make private");
      }
    } catch (e) {
      toast.error("Failed to make private");
    }
  };

  const shareToTwitter = async (backtest) => {
    const shareUrl = await ensurePublicShare(backtest);
    const text = generateShareText(backtest, shareUrl);
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank", "width=550,height=420");

    // Track share event
    logger.info("Shared to Twitter", { backtest_id: backtest.id });
    trackAnalyticsEvent("backtest_shared", { platform: "twitter", backtest_id: backtest.id });
    matomoTrackEvent("Backtesting", "Share", "twitter", 1);
  };

  const shareToLinkedIn = async (backtest) => {
    const shareUrl = await ensurePublicShare(backtest);
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
    window.open(linkedInUrl, "_blank", "width=550,height=420");

    // Track share event
    logger.info("Shared to LinkedIn", { backtest_id: backtest.id });
    trackAnalyticsEvent("backtest_shared", { platform: "linkedin", backtest_id: backtest.id });
    matomoTrackEvent("Backtesting", "Share", "linkedin", 1);
  };

  const shareToReddit = async (backtest) => {
    const shareUrl = await ensurePublicShare(backtest);
    const redditUrl = `https://www.reddit.com/submit?url=${encodeURIComponent(shareUrl)}&title=${encodeURIComponent(backtest.name + " - Backtest Results")}`;
    window.open(redditUrl, "_blank", "width=550,height=420");

    // Track share event
    logger.info("Shared to Reddit", { backtest_id: backtest.id });
    trackAnalyticsEvent("backtest_shared", { platform: "reddit", backtest_id: backtest.id });
    matomoTrackEvent("Backtesting", "Share", "reddit", 1);
  };

  const copyShareLink = async (backtest) => {
    const shareUrl = await ensurePublicShare(backtest);
    const text = generateShareText(backtest, shareUrl);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success("Copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);

      // Track copy event
      logger.info("Copied share link", { backtest_id: backtest.id });
      trackAnalyticsEvent("backtest_share_copied", { backtest_id: backtest.id });
      matomoTrackEvent("Backtesting", "Share", "copy", 1);
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  // Image export function
  const exportToImage = async () => {
    if (!exportCardRef.current) {
      toast.error("Results not available for export");
      return;
    }

    setExporting(true);
    try {
      // Ensure the QR code points to an actually public page
      if (currentBacktest) {
        await ensurePublicShare(currentBacktest);
      }

      const dataUrl = await htmlToImage.toPng(exportCardRef.current, {
        quality: 0.98,
        pixelRatio: 2, // Higher resolution for better quality
        backgroundColor: "#ffffff",
        width: exportConfig.width,
        height: exportConfig.height,
        style: {
          width: `${exportConfig.width}px`,
          height: `${exportConfig.height}px`,
        },
      });

      // Create download link
      const link = document.createElement('a');
      link.download = `${currentBacktest?.name || 'backtest'}-${exportConfig.id}-tradescanpro.png`;
      link.href = dataUrl;
      link.click();

      toast.success("Image exported successfully!");

      // Track export event
      logger.info("Exported backtest image", { backtest_id: currentBacktest?.id, preset: exportConfig.id });
      trackAnalyticsEvent("backtest_image_exported", {
        backtest_id: currentBacktest?.id,
        preset: exportConfig.id,
      });
      matomoTrackEvent("Backtesting", "Export", exportConfig.id, 1);
    } catch (err) {
      console.error('Export failed:', err);
      toast.error("Failed to export image");
    } finally {
      setExporting(false);
    }
  };

  const exportToPDF = async () => {
    if (!exportCardRef.current) {
      toast.error("Results not available for export");
      return;
    }

    setPdfExporting(true);
    try {
      if (currentBacktest) {
        await ensurePublicShare(currentBacktest);
      }

      const canvas = await html2canvas(exportCardRef.current, {
        backgroundColor: "#ffffff",
        scale: 2,
        useCORS: true,
        logging: false,
      });

      const imgData = canvas.toDataURL("image/png", 1.0);
      const orientation = exportConfig.width >= exportConfig.height ? "landscape" : "portrait";
      const pdf = new jsPDF({
        orientation,
        unit: "px",
        format: [exportConfig.width, exportConfig.height],
        compress: true,
      });

      pdf.addImage(imgData, "PNG", 0, 0, exportConfig.width, exportConfig.height, undefined, "FAST");
      pdf.save(`${currentBacktest?.name || "backtest"}-${exportConfig.id}-tradescanpro.pdf`);

      trackAnalyticsEvent("backtest_pdf_exported", {
        backtest_id: currentBacktest?.id,
        preset: exportConfig.id,
      });
      matomoTrackEvent("Backtesting", "ExportPDF", exportConfig.id, 1);
      toast.success("PDF exported successfully!");
    } catch (e) {
      toast.error("Failed to export PDF");
    } finally {
      setPdfExporting(false);
    }
  };

  const generateViralHeadline = (backtest) => {
    const r = backtest?.results || {};
    const name = backtest?.name || "my strategy";
    const totalReturn = Number(r.total_return ?? 0);
    const sharpe = Number(r.sharpe_ratio ?? 0);
    const win = Number(r.win_rate ?? 0);
    const grade = r.quality_grade || "";

    const templates = [
      totalReturn >= 50 ? `This "${name}" strategy returned ${totalReturn.toFixed(1)}% 🚀` : null,
      totalReturn >= 20 ? `I backtested "${name}" — up ${totalReturn.toFixed(1)}% 📈` : null,
      grade ? `"${name}" got a ${grade} grade in AI backtesting` : null,
      sharpe >= 2 ? `"${name}" hit Sharpe ${sharpe.toFixed(2)} (risk-adjusted beast)` : null,
      win >= 70 ? `"${name}" has a ${win.toFixed(1)}% win rate — would you trade this?` : null,
      totalReturn < 0 ? `I backtested "${name}" and it lost ${totalReturn.toFixed(1)}% — here’s what I learned` : null,
      `I backtested "${name}" with AI — results inside 👇`,
    ].filter(Boolean);

    return templates[0] || `I backtested "${name}" with AI — results inside 👇`;
  };

  const copyHeadline = async () => {
    try {
      const headline = generateViralHeadline(currentBacktest);
      await navigator.clipboard.writeText(headline);
      toast.success("Headline copied!");
      trackAnalyticsEvent("backtest_headline_copied", { backtest_id: currentBacktest?.id });
      matomoTrackEvent("Backtesting", "CopyHeadline", "copied", 1);
    } catch {
      toast.error("Failed to copy headline");
    }
  };

  const getEmbedCode = () => {
    const origin = window.location.origin;
    const slug = currentBacktest?.share_slug;
    const src = slug ? `${origin}/embed/backtest/${encodeURIComponent(slug)}` : getShareUrl(currentBacktest);
    return `<iframe src="${src}" width="600" height="420" style="border:0;border-radius:12px;overflow:hidden" loading="lazy" title="TradeScanPro Backtest"></iframe>`;
  };

  // Load backtest history
  useEffect(() => {
    loadBacktestHistory();
  }, []);

  // Load weekly challenge
  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/api/challenges/current/`);
        const data = await res.json();
        if (data?.success) setWeeklyChallenge(data.challenge);
      } catch {
        // ignore
      }
    };
    load();
  }, []);

  const loadBacktestHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await listBacktests();
      if (response.success) {
        setBacktestHistory(response.backtests || []);
      }
    } catch (error) {
      logger.error("Failed to load backtest history:", error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSelectBaseline = (strategy) => {
    setSelectedBaseline(strategy);
    setStrategyText(strategy.description);
    setBacktestName(strategy.name);
  };

  const handleCreateAndRun = async () => {
    if (!strategyText.trim()) {
      toast.error("Please describe your trading strategy");
      return;
    }
    if (!symbols.trim()) {
      toast.error("Please enter at least one symbol");
      return;
    }

    setIsLoading(true);
    try {
      // Create backtest
      const createResponse = await createBacktest({
        name: backtestName || "Custom Strategy",
        strategy_text: strategyText,
        category: category,
        symbols: symbols.split(",").map(s => s.trim().toUpperCase()),
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(initialCapital)
      });

      if (!createResponse.success) {
        toast.error(createResponse.error || "Failed to create backtest");
        setIsLoading(false);
        return;
      }

      toast.success("Backtest created! Running AI analysis...");
      setIsRunning(true);

      // Run backtest
      const runResponse = await runBacktest(createResponse.backtest_id);

      if (!runResponse.success) {
        toast.error(runResponse.error || "Backtest failed");
        setIsRunning(false);
        setIsLoading(false);
        return;
      }

      // Show achievement unlocks (if any)
      if (Array.isArray(runResponse.achievements_unlocked) && runResponse.achievements_unlocked.length > 0) {
        setAchievementQueue(runResponse.achievements_unlocked);
        setActiveAchievement(runResponse.achievements_unlocked[0]);
      }

      // Get full results
      const resultResponse = await getBacktest(createResponse.backtest_id);
      
      if (resultResponse.success) {
        setCurrentBacktest(resultResponse.backtest);
        setActiveTab("results");
        toast.success("Backtest completed!");
        loadBacktestHistory();
      }

    } catch (error) {
      logger.error("Backtest error:", error);
      toast.error(error.response?.data?.error || "An error occurred");
    } finally {
      setIsLoading(false);
      setIsRunning(false);
    }
  };

  const handleCloseAchievement = () => {
    setAchievementQueue((prev) => {
      const queue = Array.isArray(prev) ? prev : [];
      const next = queue.slice(1);
      setActiveAchievement(next.length > 0 ? next[0] : null);
      return next;
    });
  };

  const handleViewBacktest = async (backtest) => {
    try {
      const response = await getBacktest(backtest.id);
      if (response.success) {
        setCurrentBacktest(response.backtest);
        setActiveTab("results");
      }
    } catch (error) {
      toast.error("Failed to load backtest details");
    }
  };

  const toggleCompareSelection = (id) => {
    setSelectedCompareIds((prev) => {
      const current = Array.isArray(prev) ? prev : [];
      if (current.includes(id)) return current.filter((x) => x !== id);
      if (current.length >= 2) return current; // max 2
      return [...current, id];
    });
  };

  const clearCompareSelection = () => setSelectedCompareIds([]);

  const openCompare = async () => {
    if (selectedCompareIds.length !== 2) {
      toast.error("Select exactly 2 backtests to compare");
      return;
    }
    setCompareLoading(true);
    try {
      const [a, b] = await Promise.all(selectedCompareIds.map((id) => getBacktest(id)));
      if (!a?.success || !b?.success) {
        toast.error("Failed to load backtests for comparison");
        return;
      }
      setCompareBacktests([a.backtest, b.backtest]);
      setCompareOpen(true);
    } catch (e) {
      toast.error("Failed to load comparison");
    } finally {
      setCompareLoading(false);
    }
  };

  const buildComparisonEquityData = (a, b) => {
    const aa = a?.equity_curve || [];
    const bb = b?.equity_curve || [];
    const n = Math.max(aa.length, bb.length);
    return Array.from({ length: n }, (_, i) => ({
      day: i + 1,
      a: aa[i] ?? null,
      b: bb[i] ?? null,
    }));
  };

  // Format equity curve for chart
  const equityCurveData = currentBacktest?.equity_curve?.map((value, index) => ({
    day: index,
    equity: value
  })) || [];

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl" data-testid="backtesting-page">
      <SEO 
        title="AI Backtesting | Trade Scan Pro" 
        description="Test your trading strategies with AI-powered backtesting"
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Backtesting</h1>
                <p className="text-gray-500">Test your trading strategies with AI-powered analysis</p>
              </div>
            </div>
            <Badge variant="outline" className="mt-2">
              <Sparkles className="h-3 w-3 mr-1" />
              Powered by Groq AI
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => navigate("/strategies/leaderboard")}>
              <Trophy className="h-4 w-4 mr-2 text-yellow-600" />
              Strategy Leaderboard
            </Button>
          </div>
        </div>

        {weeklyChallenge && (
          <Card className="mt-4 border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
            <CardContent className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-purple-800">This week’s challenge</div>
                <div className="text-lg font-bold text-gray-900">{weeklyChallenge.title}</div>
                <div className="text-sm text-gray-600">
                  Target: {weeklyChallenge.target?.threshold}{weeklyChallenge.target?.unit} {weeklyChallenge.target?.metric?.replace(/_/g, " ")}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" onClick={() => navigate("/app/backtesting")}>
                  Enter Challenge
                </Button>
                <Button variant="outline" onClick={() => window.open("/api/challenges/leaderboard/", "_blank")}>
                  View Leaderboard
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
          <TabsTrigger value="create" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Create Strategy
          </TabsTrigger>
          <TabsTrigger value="results" className="flex items-center gap-2" disabled={!currentBacktest}>
            <BarChart3 className="h-4 w-4" />
            Results
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Create Strategy Tab */}
        <TabsContent value="create" className="space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column - Strategy Input */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-blue-500" />
                    Describe Your Strategy
                  </CardTitle>
                  <CardDescription>
                    Write your trading strategy in plain English. Our AI will convert it to executable code.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="strategy-name">Strategy Name</Label>
                    <Input
                      id="strategy-name"
                      placeholder="My Trading Strategy"
                      value={backtestName}
                      onChange={(e) => setBacktestName(e.target.value)}
                      data-testid="strategy-name-input"
                    />
                  </div>

                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select value={category} onValueChange={setCategory}>
                      <SelectTrigger data-testid="category-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="day_trading">Day Trading</SelectItem>
                        <SelectItem value="swing_trading">Swing Trading</SelectItem>
                        <SelectItem value="long_term">Long-Term Investing</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="strategy-text">Strategy Description</Label>
                    <Textarea
                      id="strategy-text"
                      placeholder="Example: Buy when the 20-day EMA crosses above the 50-day EMA. Sell when the 20-day EMA crosses below the 50-day EMA. Use a 5% stop-loss."
                      value={strategyText}
                      onChange={(e) => setStrategyText(e.target.value)}
                      rows={6}
                      className="resize-none"
                      data-testid="strategy-text-input"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Include entry conditions, exit conditions, stop-loss, and take-profit rules.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="symbols">Symbols</Label>
                      <Input
                        id="symbols"
                        placeholder="AAPL, MSFT, GOOGL"
                        value={symbols}
                        onChange={(e) => setSymbols(e.target.value)}
                        data-testid="symbols-input"
                      />
                      <p className="text-xs text-gray-500 mt-1">Comma-separated</p>
                    </div>
                    <div>
                      <Label htmlFor="capital">Initial Capital ($)</Label>
                      <Input
                        id="capital"
                        type="number"
                        value={initialCapital}
                        onChange={(e) => setInitialCapital(e.target.value)}
                        data-testid="capital-input"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="start-date">Start Date</Label>
                      <Input
                        id="start-date"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        data-testid="start-date-input"
                      />
                    </div>
                    <div>
                      <Label htmlFor="end-date">End Date</Label>
                      <Input
                        id="end-date"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        data-testid="end-date-input"
                      />
                    </div>
                  </div>

                  <Button 
                    className="w-full" 
                    size="lg"
                    onClick={handleCreateAndRun}
                    disabled={isLoading || isRunning}
                    data-testid="run-backtest-btn"
                  >
                    {isLoading || isRunning ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        {isRunning ? "Running Backtest..." : "Creating..."}
                      </>
                    ) : (
                      <>
                        <Play className="h-5 w-5 mr-2" />
                        Run Backtest
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Baseline Strategies */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-500" />
                    Baseline Strategies
                  </CardTitle>
                  <CardDescription>
                    Choose a pre-built strategy as a starting point
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 max-h-[600px] overflow-y-auto">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm text-gray-700">{CATEGORY_LABELS[category]}</h4>
                    {BASELINE_STRATEGIES[category]?.map((strategy) => (
                      <StrategyCard
                        key={strategy.id}
                        strategy={strategy}
                        selected={selectedBaseline?.id === strategy.id}
                        onSelect={handleSelectBaseline}
                      />
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {currentBacktest ? (
            <div ref={resultsCardRef}>
              {/* Offscreen export template (fixed size for social) */}
              <div
                className="fixed left-[-10000px] top-0"
                style={{ width: exportConfig.width, height: exportConfig.height }}
                aria-hidden="true"
              >
                <div
                  ref={exportCardRef}
                  style={{ width: exportConfig.width, height: exportConfig.height }}
                  className="bg-white overflow-hidden border border-gray-200"
                >
                  <div className="h-full w-full flex flex-col">
                    {/* Header */}
                    <div className="px-10 pt-8 pb-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="text-sm font-semibold tracking-wide opacity-90">TradeScanPro</div>
                          <div className="text-3xl font-bold leading-tight mt-1">
                            {currentBacktest.name}
                          </div>
                          <div className="text-sm opacity-90 mt-2">
                            {CATEGORY_LABELS[currentBacktest.category]} • {currentBacktest.symbols?.join(", ")}
                          </div>
                        </div>
                        <div className="bg-white rounded-xl p-3 shadow-sm">
                          <QRCodeCanvas
                            value={getShareUrlForExport(currentBacktest)}
                            size={exportConfig.id === "twitter" ? 120 : 140}
                            includeMargin
                          />
                        </div>
                      </div>
                    </div>

                    {/* Body */}
                    <div className="flex-1 px-10 py-8">
                      <div className="grid grid-cols-4 gap-4">
                        <div className="rounded-xl border border-gray-200 p-4">
                          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Total Return</div>
                          <div className={`text-3xl font-bold mt-2 ${currentBacktest.results?.total_return >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {currentBacktest.results?.total_return >= 0 ? "+" : ""}{currentBacktest.results?.total_return?.toFixed(1) || 0}%
                          </div>
                        </div>
                        <div className="rounded-xl border border-gray-200 p-4">
                          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Sharpe</div>
                          <div className="text-3xl font-bold mt-2 text-gray-900">
                            {currentBacktest.results?.sharpe_ratio?.toFixed(2) || "0.00"}
                          </div>
                        </div>
                        <div className="rounded-xl border border-gray-200 p-4">
                          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Win Rate</div>
                          <div className="text-3xl font-bold mt-2 text-gray-900">
                            {currentBacktest.results?.win_rate?.toFixed(1) || 0}%
                          </div>
                        </div>
                        <div className="rounded-xl border border-gray-200 p-4">
                          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Quality</div>
                          <div className="text-3xl font-bold mt-2 text-gray-900">
                            {currentBacktest.results?.quality_grade || "N/A"}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {currentBacktest.results?.composite_score?.toFixed(1) || 0}/100
                          </div>
                        </div>
                      </div>

                      <div className="mt-8 rounded-xl bg-gray-50 border border-gray-200 p-5">
                        <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">Share text</div>
                        <div className="text-sm text-gray-700 whitespace-pre-line font-mono">
                          {generateShareText(currentBacktest)}
                        </div>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="px-10 py-5 border-t border-gray-200 flex items-center justify-between">
                      <div className="text-sm text-gray-600">
                        Scan. Backtest. Improve.
                      </div>
                      <div className="text-sm font-semibold text-gray-900">
                        TradeScanPro.com
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Results Header */}
              <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-0">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold">{currentBacktest.name}</h2>
                      <p className="text-gray-600">{CATEGORY_LABELS[currentBacktest.category]}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline">{currentBacktest.symbols?.join(", ")}</Badge>
                        <Badge variant="outline">
                          <Clock className="h-3 w-3 mr-1" />
                          {currentBacktest.start_date} to {currentBacktest.end_date}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold">
                        <span className={currentBacktest.results?.composite_score >= 50 ? "text-green-600" : "text-red-600"}>
                          {currentBacktest.results?.composite_score?.toFixed(1) || 0}
                        </span>
                        <span className="text-lg text-gray-400">/100</span>
                      </div>
                      <p className="text-sm text-gray-500">Composite Score</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <MetricCard
                  title="Total Return"
                  value={`${currentBacktest.results?.total_return >= 0 ? "+" : ""}${currentBacktest.results?.total_return?.toFixed(2) || 0}%`}
                  icon={TrendingUp}
                  color={currentBacktest.results?.total_return >= 0 ? "green" : "red"}
                />
                <MetricCard
                  title="Sharpe Ratio"
                  value={currentBacktest.results?.sharpe_ratio?.toFixed(2) || "0.00"}
                  subtitle="Risk-adjusted"
                  icon={Target}
                  color="blue"
                />
                <MetricCard
                  title="Max Drawdown"
                  value={`${currentBacktest.results?.max_drawdown?.toFixed(2) || 0}%`}
                  icon={TrendingDown}
                  color="red"
                />
                <MetricCard
                  title="Win Rate"
                  value={`${currentBacktest.results?.win_rate?.toFixed(1) || 0}%`}
                  subtitle={`${currentBacktest.results?.winning_trades || 0}/${currentBacktest.results?.total_trades || 0} trades`}
                  icon={Trophy}
                  color={currentBacktest.results?.win_rate >= 50 ? "green" : "yellow"}
                />
                <MetricCard
                  title="Profit Factor"
                  value={currentBacktest.results?.profit_factor?.toFixed(2) || "0.00"}
                  icon={DollarSign}
                  color={currentBacktest.results?.profit_factor >= 1 ? "green" : "red"}
                />
              </div>

              {/* Suggested viral headline */}
              <Card className="border-2 border-purple-100 bg-gradient-to-r from-purple-50/60 to-pink-50/60">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between gap-3">
                    <span className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-purple-600" />
                      Suggested Share Headline
                    </span>
                    <Button variant="outline" size="sm" onClick={copyHeadline}>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                  </CardTitle>
                  <CardDescription>
                    Use this headline to improve click-through when sharing.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="p-4 bg-white rounded-lg border border-dashed border-purple-200">
                    <p className="text-base font-semibold text-gray-900">
                      {generateViralHeadline(currentBacktest)}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Social Sharing Section */}
              <Card className="border-2 border-blue-100 bg-gradient-to-r from-blue-50/50 to-purple-50/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Share2 className="h-5 w-5 text-blue-500" />
                    Share Your Results
                  </CardTitle>
                  <CardDescription>
                    Show your trading strategy performance to the world
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Public/private toggle */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={currentBacktest.is_public ? "border-green-300 text-green-700 bg-green-50" : "border-gray-300 text-gray-700 bg-white"}>
                        {currentBacktest.is_public ? "Public" : "Private"}
                      </Badge>
                      <span className="text-xs text-gray-600">
                        {currentBacktest.is_public ? "Anyone with the link can view." : "Only you can view."}
                      </span>
                    </div>
                    {currentBacktest.is_public ? (
                      <Button variant="outline" size="sm" onClick={() => setPrivateShare(currentBacktest)}>
                        Make Private
                      </Button>
                    ) : (
                      <Button size="sm" onClick={() => ensurePublicShare(currentBacktest).then(() => toast.success("Public share link created"))}>
                        Make Public Link
                      </Button>
                    )}
                  </div>

                  {/* Export preset */}
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <div className="w-full sm:w-[280px]">
                      <Select value={exportPreset} onValueChange={setExportPreset}>
                        <SelectTrigger>
                          <Image className="h-4 w-4 mr-2 text-purple-600" />
                          <SelectValue placeholder="Export preset" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="twitter">{EXPORT_PRESETS.twitter.label}</SelectItem>
                          <SelectItem value="instagram_square">{EXPORT_PRESETS.instagram_square.label}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="text-xs text-gray-600">
                      Includes a QR code linking to the public share page.
                    </div>
                  </div>

                  {/* Share Buttons */}
                  <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                    <Button
                      variant="outline"
                      className="w-full hover:bg-blue-50 hover:border-blue-300 transition-all"
                      onClick={() => shareToTwitter(currentBacktest)}
                    >
                      <Twitter className="h-4 w-4 mr-2 text-blue-500" />
                      Twitter/X
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full hover:bg-blue-50 hover:border-blue-300 transition-all"
                      onClick={() => shareToLinkedIn(currentBacktest)}
                    >
                      <Linkedin className="h-4 w-4 mr-2 text-blue-700" />
                      LinkedIn
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full hover:bg-orange-50 hover:border-orange-300 transition-all"
                      onClick={() => shareToReddit(currentBacktest)}
                    >
                      <Share className="h-4 w-4 mr-2 text-orange-500" />
                      Reddit
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full hover:bg-green-50 hover:border-green-300 transition-all"
                      onClick={() => copyShareLink(currentBacktest)}
                    >
                      {copied ? (
                        <>
                          <Check className="h-4 w-4 mr-2 text-green-500" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2 text-gray-600" />
                          Copy Text
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full hover:bg-purple-50 hover:border-purple-300 transition-all"
                      onClick={exportToImage}
                      disabled={exporting}
                    >
                      {exporting ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 text-purple-500 animate-spin" />
                          Exporting...
                        </>
                      ) : (
                        <>
                          <Download className="h-4 w-4 mr-2 text-purple-600" />
                          Export PNG
                        </>
                      )}
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full hover:bg-purple-50 hover:border-purple-300 transition-all"
                      onClick={exportToPDF}
                      disabled={pdfExporting}
                    >
                      {pdfExporting ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 text-purple-500 animate-spin" />
                          PDF…
                        </>
                      ) : (
                        <>
                          <FileText className="h-4 w-4 mr-2 text-purple-600" />
                          Export PDF
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Share Preview */}
                  <div className="p-4 bg-white rounded-lg border-2 border-dashed border-gray-200">
                    <p className="text-xs text-gray-600 mb-2 font-semibold uppercase tracking-wide">
                      Share preview:
                    </p>
                    <p className="text-sm text-gray-700 whitespace-pre-line font-mono bg-gray-50 p-3 rounded border">
                      {generateShareText(currentBacktest)}
                    </p>
                  </div>

                  {/* Share Stats (optional - for future enhancement) */}
                  <div className="flex items-center justify-center gap-6 pt-2 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Share2 className="h-3 w-3" />
                      <span>Share to grow the community</span>
                    </div>
                  </div>

                  {/* Embed */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-2">
                    <div className="text-xs text-gray-600">
                      Want to embed this result on a blog or website?
                    </div>
                    <Button
                      variant="outline"
                      onClick={async () => {
                        await ensurePublicShare(currentBacktest);
                        setEmbedOpen(true);
                      }}
                    >
                      <Code className="h-4 w-4 mr-2" />
                      Embed
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Equity Curve Chart */}
              {equityCurveData.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <LineChart className="h-5 w-5 text-blue-500" />
                      Equity Curve
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={equityCurveData}>
                          <defs>
                            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis
                            dataKey="day"
                            stroke="#9CA3AF"
                            tick={{ fontSize: 12 }}
                          />
                          <YAxis
                            stroke="#9CA3AF"
                            tick={{ fontSize: 12 }}
                            tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`}
                          />
                          <Tooltip
                            formatter={(value) => [`$${value.toFixed(2)}`, "Portfolio Value"]}
                            contentStyle={{ borderRadius: 8, border: "1px solid #E5E7EB" }}
                          />
                          <Area
                            type="monotone"
                            dataKey="equity"
                            stroke="#3B82F6"
                            strokeWidth={2}
                            fill="url(#equityGradient)"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Advanced Metrics - Help Users Judge Strategy Quality */}
              {currentBacktest.results && (
                <Card className="border-2 border-purple-100 bg-gradient-to-r from-purple-50/30 to-pink-50/30">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-purple-500" />
                      Advanced Metrics
                      <Badge variant="outline" className="ml-2 bg-purple-100 text-purple-700 border-purple-300">
                        {currentBacktest.results.quality_grade || 'N/A'}
                      </Badge>
                    </CardTitle>
                    <CardDescription>
                      Deep dive into your strategy's risk profile and statistical significance
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Risk-Adjusted Returns */}
                    <div>
                      <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-blue-500" />
                        Risk-Adjusted Returns
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Sortino Ratio</p>
                          <p className="text-lg font-bold text-blue-600">
                            {currentBacktest.results.sortino_ratio?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-xs text-gray-400">Downside risk only</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Calmar Ratio</p>
                          <p className="text-lg font-bold text-green-600">
                            {currentBacktest.results.calmar_ratio?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-xs text-gray-400">Return / Max DD</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Omega Ratio</p>
                          <p className="text-lg font-bold text-purple-600">
                            {currentBacktest.results.omega_ratio?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-xs text-gray-400">Gains vs losses</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Recovery Factor</p>
                          <p className="text-lg font-bold text-indigo-600">
                            {currentBacktest.results.recovery_factor?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-xs text-gray-400">Profit / Drawdown</p>
                        </div>
                      </div>
                    </div>

                    {/* Downside Risk Metrics */}
                    <div>
                      <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                        <TrendingDown className="h-4 w-4 text-red-500" />
                        Downside Risk Analysis
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Ulcer Index</p>
                          <p className="text-lg font-bold text-red-600">
                            {currentBacktest.results.ulcer_index?.toFixed(2) || '0.00'}%
                          </p>
                          <p className="text-xs text-gray-400">Stress measure</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">VaR (95%)</p>
                          <p className="text-lg font-bold text-orange-600">
                            {currentBacktest.results.var_95?.toFixed(2) || '0.00'}%
                          </p>
                          <p className="text-xs text-gray-400">Worst 5% day</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">CVaR (95%)</p>
                          <p className="text-lg font-bold text-red-700">
                            {currentBacktest.results.cvar_95?.toFixed(2) || '0.00'}%
                          </p>
                          <p className="text-xs text-gray-400">Expected tail loss</p>
                        </div>
                      </div>
                    </div>

                    {/* Trade Quality Analysis */}
                    <div>
                      <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                        <Trophy className="h-4 w-4 text-yellow-500" />
                        Trade Quality
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Avg Win</p>
                          <p className="text-lg font-bold text-green-600">
                            +{currentBacktest.results.avg_win?.toFixed(2) || '0.00'}%
                          </p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Avg Loss</p>
                          <p className="text-lg font-bold text-red-600">
                            {currentBacktest.results.avg_loss?.toFixed(2) || '0.00'}%
                          </p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Expectancy</p>
                          <p className={`text-lg font-bold ${currentBacktest.results.expectancy >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {currentBacktest.results.expectancy >= 0 ? '+' : ''}{currentBacktest.results.expectancy?.toFixed(2) || '0.00'}%
                          </p>
                          <p className="text-xs text-gray-400">Per trade avg</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Kelly Criterion</p>
                          <p className="text-lg font-bold text-blue-600">
                            {currentBacktest.results.kelly_criterion?.toFixed(1) || '0.0'}%
                          </p>
                          <p className="text-xs text-gray-400">Optimal position</p>
                        </div>
                      </div>
                    </div>

                    {/* Consistency Metrics */}
                    <div>
                      <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                        <BarChart3 className="h-4 w-4 text-indigo-500" />
                        Consistency
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-2 gap-3">
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Max Consecutive Wins</p>
                          <p className="text-lg font-bold text-green-600">
                            {currentBacktest.results.max_consecutive_wins || 0}
                          </p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">Max Consecutive Losses</p>
                          <p className="text-lg font-bold text-red-600">
                            {currentBacktest.results.max_consecutive_losses || 0}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Statistical Significance */}
                    <div>
                      <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-purple-500" />
                        Statistical Significance
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-2 gap-3">
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">T-Statistic</p>
                          <p className="text-lg font-bold text-purple-600">
                            {currentBacktest.results.t_statistic?.toFixed(2) || '0.00'}
                          </p>
                          <p className="text-xs text-gray-400">Returns vs zero</p>
                        </div>
                        <div className="p-3 bg-white rounded-lg border">
                          <p className="text-xs text-gray-500">P-Value</p>
                          <p className={`text-lg font-bold ${currentBacktest.results.p_value < 0.05 ? 'text-green-600' : 'text-gray-600'}`}>
                            {currentBacktest.results.p_value?.toFixed(4) || '1.0000'}
                          </p>
                          <p className="text-xs text-gray-400">
                            {currentBacktest.results.p_value < 0.05 ? 'Significant!' : 'Not significant'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Quality Interpretation */}
                    <Alert className={`${
                      currentBacktest.results.quality_grade === 'A+' || currentBacktest.results.quality_grade === 'A' ? 'bg-green-50 border-green-200' :
                      currentBacktest.results.quality_grade === 'B' ? 'bg-blue-50 border-blue-200' :
                      currentBacktest.results.quality_grade === 'C' ? 'bg-yellow-50 border-yellow-200' :
                      'bg-red-50 border-red-200'
                    }`}>
                      <AlertCircle className={`h-4 w-4 ${
                        currentBacktest.results.quality_grade === 'A+' || currentBacktest.results.quality_grade === 'A' ? 'text-green-600' :
                        currentBacktest.results.quality_grade === 'B' ? 'text-blue-600' :
                        currentBacktest.results.quality_grade === 'C' ? 'text-yellow-600' :
                        'text-red-600'
                      }`} />
                      <AlertDescription className="text-sm">
                        <strong>Strategy Quality: {currentBacktest.results.quality_grade}</strong>
                        <br />
                        {currentBacktest.results.quality_grade === 'A+' && 'Exceptional strategy with strong risk-adjusted returns and statistical significance.'}
                        {currentBacktest.results.quality_grade === 'A' && 'Excellent strategy with solid metrics across the board.'}
                        {currentBacktest.results.quality_grade === 'B' && 'Good strategy but room for improvement in risk management or consistency.'}
                        {currentBacktest.results.quality_grade === 'C' && 'Mediocre strategy. Consider refining entry/exit rules.'}
                        {(currentBacktest.results.quality_grade === 'D' || currentBacktest.results.quality_grade === 'F') && 'Poor strategy. Significant improvements needed before live trading.'}
                      </AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              )}

              {/* Trade History */}
              {currentBacktest.trades?.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Trade History</CardTitle>
                    <CardDescription>{currentBacktest.trades.length} trades executed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-2 px-3 font-medium text-gray-500">Entry Date</th>
                            <th className="text-left py-2 px-3 font-medium text-gray-500">Exit Date</th>
                            <th className="text-right py-2 px-3 font-medium text-gray-500">Entry Price</th>
                            <th className="text-right py-2 px-3 font-medium text-gray-500">Exit Price</th>
                            <th className="text-right py-2 px-3 font-medium text-gray-500">Return</th>
                          </tr>
                        </thead>
                        <tbody>
                          {currentBacktest.trades.slice(0, 20).map((trade, index) => (
                            <tr key={index} className="border-b hover:bg-gray-50">
                              <td className="py-2 px-3">{trade.entry_date?.split("T")[0]}</td>
                              <td className="py-2 px-3">{trade.exit_date?.split("T")[0]}</td>
                              <td className="py-2 px-3 text-right">${trade.entry_price?.toFixed(2)}</td>
                              <td className="py-2 px-3 text-right">${trade.exit_price?.toFixed(2)}</td>
                              <td className={`py-2 px-3 text-right font-medium ${trade.return_pct >= 0 ? "text-green-600" : "text-red-600"}`}>
                                {trade.return_pct >= 0 ? "+" : ""}{trade.return_pct?.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Generated Code (collapsible) */}
              {currentBacktest.generated_code && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-purple-500" />
                      AI-Generated Strategy Code
                    </CardTitle>
                    <CardDescription>Python code generated by Groq AI</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{currentBacktest.generated_code}</code>
                    </pre>
                  </CardContent>
                </Card>
              )}

              {/* Watermark for export */}
              <div className="mt-6 text-center pb-4">
                <p className="text-sm text-gray-500 font-medium">
                  Generated with TradeScanPro.com
                </p>
              </div>
            </div>
          ) : (
            <Card className="p-12 text-center">
              <BarChart3 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No Results Yet</h3>
              <p className="text-gray-500 mt-1">Create and run a backtest to see results here</p>
              <Button className="mt-4" onClick={() => setActiveTab("create")}>
                Create Strategy
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Backtest History</CardTitle>
              <CardDescription>View your past backtest results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <div className="text-sm text-gray-600">
                  Select 2 items to compare. ({selectedCompareIds.length}/2 selected)
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    disabled={selectedCompareIds.length === 0}
                    onClick={clearCompareSelection}
                  >
                    Clear
                  </Button>
                  <Button
                    disabled={selectedCompareIds.length !== 2 || compareLoading}
                    onClick={openCompare}
                  >
                    {compareLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Loading…
                      </>
                    ) : (
                      <>
                        Compare
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {historyLoading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
              ) : backtestHistory.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {backtestHistory.map((backtest) => (
                    <BacktestHistoryItem
                      key={backtest.id}
                      backtest={backtest}
                      onView={handleViewBacktest}
                      selectedForCompare={selectedCompareIds.includes(backtest.id)}
                      onToggleCompare={toggleCompareSelection}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center p-8">
                  <History className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">No History Yet</h3>
                  <p className="text-gray-500 mt-1">Your backtest history will appear here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Comparison dialog */}
      <Dialog open={compareOpen} onOpenChange={setCompareOpen}>
        <DialogContent className="max-w-5xl">
          <DialogHeader>
            <DialogTitle>Strategy Comparison</DialogTitle>
            <DialogDescription>
              Side-by-side comparison of two backtests.
            </DialogDescription>
          </DialogHeader>

          {compareBacktests.length === 2 ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {compareBacktests.map((bt, idx) => (
                  <Card key={bt.id}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between gap-3">
                        <span className="truncate">{bt.name}</span>
                        <Badge variant="outline">{bt.results?.quality_grade || "N/A"}</Badge>
                      </CardTitle>
                      <CardDescription>
                        {CATEGORY_LABELS[bt.category]} • {bt.symbols?.join(", ")}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Total return</div>
                        <div className="text-xl font-bold">
                          {bt.results?.total_return >= 0 ? "+" : ""}{bt.results?.total_return?.toFixed(2) || 0}%
                        </div>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Composite score</div>
                        <div className="text-xl font-bold">
                          {bt.results?.composite_score?.toFixed(1) || 0}/100
                        </div>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Sharpe</div>
                        <div className="text-xl font-bold">
                          {bt.results?.sharpe_ratio?.toFixed(2) || "0.00"}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Max drawdown</div>
                        <div className="text-xl font-bold">
                          {bt.results?.max_drawdown?.toFixed(2) || 0}%
                        </div>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Win rate</div>
                        <div className="text-xl font-bold">
                          {bt.results?.win_rate?.toFixed(1) || 0}%
                        </div>
                      </div>
                      <div className="p-3 rounded-lg border">
                        <div className="text-xs text-gray-500">Profit factor</div>
                        <div className="text-xl font-bold">
                          {bt.results?.profit_factor?.toFixed(2) || "0.00"}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Overlay equity curves */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LineChart className="h-5 w-5 text-blue-500" />
                    Equity Curves (Overlay)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[320px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={buildComparisonEquityData(compareBacktests[0], compareBacktests[1])}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="a" stroke="#3B82F6" dot={false} name={compareBacktests[0].name} />
                        <Line type="monotone" dataKey="b" stroke="#10B981" dot={false} name={compareBacktests[1].name} />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-sm text-gray-600">Select 2 backtests to compare.</div>
          )}
        </DialogContent>
      </Dialog>

      {/* Embed dialog */}
      <Dialog open={embedOpen} onOpenChange={setEmbedOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Embed this backtest</DialogTitle>
            <DialogDescription>
              Copy the iframe code below and paste it into your site.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <Textarea readOnly rows={4} value={getEmbedCode()} />
            <div className="flex items-center justify-end gap-2">
              <Button
                variant="outline"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(getEmbedCode());
                    toast.success("Embed code copied!");
                    trackAnalyticsEvent("backtest_embed_copied", { backtest_id: currentBacktest?.id });
                    matomoTrackEvent("Backtesting", "Embed", "copied", 1);
                  } catch {
                    toast.error("Failed to copy embed code");
                  }
                }}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy code
              </Button>
              <Button onClick={() => setEmbedOpen(false)}>Done</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* AI Disclaimer */}
      <Alert className="mt-6 bg-blue-50 border-blue-200">
        <AlertCircle className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-700">
          <strong>Disclaimer:</strong> Backtesting results are based on historical data and do not guarantee future performance. 
          AI-generated strategies should be reviewed carefully before live trading.
        </AlertDescription>
      </Alert>

      {/* Achievement unlock modal */}
      {activeAchievement && (
        <AchievementUnlock
          achievement={activeAchievement}
          onClose={handleCloseAchievement}
        />
      )}
    </div>
  );
}
