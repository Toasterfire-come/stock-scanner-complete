import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import {
  TrendingUp,
  Target,
  BarChart3,
  TrendingDown,
  Calendar,
  DollarSign,
  Percent,
  Activity,
  Award,
  ExternalLink,
  Share2,
  Twitter,
  Linkedin
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { toast } from "sonner";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function PublicBacktestShare() {
  const { backtest_id, shareSlug } = useParams();
  const navigate = useNavigate();
  const [backtest, setBacktest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const idOrSlug = shareSlug || backtest_id;
  const isNumericId = /^\d+$/.test(String(idOrSlug || ""));

  useEffect(() => {
    fetchPublicBacktest();
  }, [idOrSlug]);

  const fetchPublicBacktest = async () => {
    try {
      setLoading(true);
      const endpoint = isNumericId
        ? `${API_BASE_URL}/api/backtesting/public/${idOrSlug}/`
        : `${API_BASE_URL}/api/share/backtests/${encodeURIComponent(idOrSlug)}/`;

      const response = await fetch(endpoint);
      const data = await response.json();

      if (!data.success) {
        setError(data.error || "Backtest not found");
        return;
      }

      setBacktest(data.backtest);
    } catch (err) {
      console.error("Error fetching public backtest:", err);
      setError("Failed to load backtest");
    } finally {
      setLoading(false);
    }
  };

  const getQualityGrade = (score) => {
    if (!score) return "N/A";
    if (score >= 90) return "A+";
    if (score >= 80) return "A";
    if (score >= 70) return "B";
    if (score >= 60) return "C";
    if (score >= 50) return "D";
    return "F";
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case "A+":
      case "A":
        return "bg-green-100 text-green-800 border-green-300";
      case "B":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "C":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "D":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "F":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const shareToTwitter = () => {
    const text = `Check out this ${backtest?.results?.quality_grade || ""} strategy on TradeScanPro: "${backtest?.name}" - ${backtest?.results?.total_return?.toFixed(1)}% returns`;
    const url = window.location.href;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, "_blank");
  };

  const shareToLinkedIn = () => {
    const url = window.location.href;
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, "_blank");
  };

  const copyShareLink = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success("Link copied to clipboard!");
  };

  const copyStrategyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(backtest?.strategy_text || "");
      toast.success("Strategy prompt copied!");
    } catch {
      toast.error("Failed to copy strategy prompt");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading backtest results...</p>
        </div>
      </div>
    );
  }

  if (error || !backtest) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <Helmet>
          <title>Backtest Not Found | TradeScanPro</title>
          <meta name="robots" content="noindex,nofollow" />
        </Helmet>
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Backtest Not Found</h1>
          <p className="text-gray-600 mb-6">{error || "This backtest doesn't exist or is not public."}</p>
          <Button onClick={() => navigate("/")}>Go to Homepage</Button>
        </div>
      </div>
    );
  }

  const results = backtest.results || {};
  const qualityGrade = getQualityGrade(results.composite_score);
  const gradeColor = getGradeColor(qualityGrade);

  // Prepare equity curve data for chart
  const equityData = (backtest.equity_curve || []).map((value, index) => ({
    day: index + 1,
    equity: value
  }));

  // Generate meta tags for social sharing
  const shareTitle = `${backtest.name} - ${qualityGrade} Strategy on TradeScanPro`;
  const shareDescription = `Backtested ${backtest.category.replace(/_/g, " ")} strategy with ${results.total_return?.toFixed(1)}% returns, ${results.win_rate?.toFixed(1)}% win rate, and ${results.sharpe_ratio?.toFixed(2)} Sharpe ratio.`;
  const shareUrl = window.location.href;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <Helmet>
        <title>{shareTitle}</title>
        <meta name="description" content={shareDescription} />

        {/* Open Graph / Facebook */}
        <meta property="og:type" content="article" />
        <meta property="og:url" content={shareUrl} />
        <meta property="og:title" content={shareTitle} />
        <meta property="og:description" content={shareDescription} />
        <meta property="og:site_name" content="TradeScanPro" />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:url" content={shareUrl} />
        <meta name="twitter:title" content={shareTitle} />
        <meta name="twitter:description" content={shareDescription} />
        <meta name="twitter:site" content="@TradeScanPro" />

        {/* Additional SEO */}
        <meta name="keywords" content={`backtesting, ${backtest.category}, trading strategy, ${backtest.symbols?.join(", ")}`} />
        <link rel="canonical" href={shareUrl} />
      </Helmet>

      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">TradeScanPro</h1>
                <p className="text-sm text-gray-500">AI-Powered Backtesting</p>
              </div>
            </div>
            <Button onClick={() => navigate("/auth/sign-up")} className="bg-blue-600 hover:bg-blue-700">
              Try It Yourself <ExternalLink className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Strategy Header */}
        <Card className="mb-6 border-2">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <CardTitle className="text-3xl">{backtest.name}</CardTitle>
                  <Badge className={`${gradeColor} text-lg px-3 py-1 font-bold`}>
                    {qualityGrade}
                  </Badge>
                </div>
                {backtest.creator?.username && (
                  <div className="text-sm text-gray-500 mb-2">
                    by <a className="underline" href={`/u/${encodeURIComponent(backtest.creator.username)}`}>@{backtest.creator.username}</a>
                  </div>
                )}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Target className="h-4 w-4" />
                    <span className="capitalize">{backtest.category?.replace(/_/g, " ")}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{backtest.start_date} to {backtest.end_date}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Activity className="h-4 w-4" />
                    <span>{backtest.symbols?.join(", ")}</span>
                  </div>
                </div>
              </div>

              {/* Share Buttons */}
              <div className="flex flex-wrap gap-2 justify-end">
                <Button variant="outline" size="sm" onClick={copyStrategyPrompt}>
                  Copy Strategy
                </Button>
                <Button variant="outline" size="sm" onClick={shareToTwitter}>
                  <Twitter className="h-4 w-4 text-blue-500" />
                </Button>
                <Button variant="outline" size="sm" onClick={shareToLinkedIn}>
                  <Linkedin className="h-4 w-4 text-blue-700" />
                </Button>
                <Button variant="outline" size="sm" onClick={copyShareLink}>
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  {results.total_return >= 0 ? (
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  ) : (
                    <TrendingDown className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {results.total_return?.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Total Return</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Activity className="h-5 w-5 text-blue-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">
                  {results.sharpe_ratio?.toFixed(2) || "N/A"}
                </p>
                <p className="text-xs text-gray-500 mt-1">Sharpe Ratio</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <TrendingDown className="h-5 w-5 text-orange-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">
                  {results.max_drawdown?.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Max Drawdown</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Percent className="h-5 w-5 text-purple-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">
                  {results.win_rate?.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">Win Rate</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Award className="h-5 w-5 text-yellow-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">
                  {results.profit_factor?.toFixed(2) || "N/A"}
                </p>
                <p className="text-xs text-gray-500 mt-1">Profit Factor</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Equity Curve */}
        {equityData.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                Equity Curve
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={equityData}>
                  <defs>
                    <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="day" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="equity"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fill="url(#equityGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* CTA Section */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
          <CardContent className="py-8 text-center">
            <h2 className="text-3xl font-bold mb-3">Create Your Own Strategy</h2>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Join TradeScanPro to backtest your trading strategies with AI-powered analysis.
              Get advanced metrics, quality grades, and instant feedback.
            </p>
            <Button
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 font-semibold"
              onClick={() => navigate("/auth/sign-up")}
            >
              Start Free Trial
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Powered by{" "}
            <a href="/" className="text-blue-600 hover:underline font-medium">
              TradeScanPro.com
            </a>
            {" "}• AI-Powered Trading Analysis
          </p>
        </div>
      </div>
    </div>
  );
}
