import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Alert, AlertDescription } from "../../components/ui/alert";
import {
  Copy,
  Loader2,
  AlertCircle,
  User,
  Calendar,
  Briefcase,
  Share2,
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
} from "lucide-react";
import { toast } from "sonner";
import { getSharedPortfolio, copySharedPortfolio } from "../../api/client";
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import SEO from "../../components/SEO";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"];

export default function SharedPortfolio() {
  const { slug } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    loadPortfolio();
  }, [slug]);

  const loadPortfolio = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSharedPortfolio(slug);
      if (data?.success) {
        setPortfolio(data.portfolio || data.data);
      } else {
        setError(data?.message || "Portfolio not found");
      }
    } catch (err) {
      setError("Unable to load portfolio");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    setCopying(true);
    try {
      const result = await copySharedPortfolio(slug);
      if (result?.success) {
        toast.success("Portfolio copied to your account!");
      } else {
        toast.error(result?.message || "Failed to copy portfolio");
      }
    } catch {
      toast.error("Please sign in to copy this portfolio");
    } finally {
      setCopying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <Loader2 className="h-12 w-12 mx-auto animate-spin text-blue-500 mb-4" />
        <p className="text-gray-500">Loading shared portfolio...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-2xl">
        <SEO title="Portfolio Not Found | Trade Scan Pro" robots="noindex" />
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="text-center mt-6">
          <Link to="/">
            <Button>Go to Homepage</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const allocationData = portfolio?.holdings?.map((h, i) => ({
    name: h.symbol,
    value: h.market_value || h.shares * (h.current_price || 0),
  })) || [];

  const totalValue = allocationData.reduce((sum, item) => sum + item.value, 0);
  const totalReturn = portfolio?.total_return || 0;
  const badges = [];
  if (totalReturn >= 20) badges.push({ label: "Market Beater", className: "bg-green-100 text-green-700" });
  if (totalReturn >= 50) badges.push({ label: "High Performer", className: "bg-purple-100 text-purple-700" });
  if ((portfolio?.holdings?.length || 0) >= 10) badges.push({ label: "Diversified", className: "bg-blue-100 text-blue-700" });

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl" data-testid="shared-portfolio-page">
      <SEO 
        title={`${portfolio?.name || "Shared Portfolio"} | Trade Scan Pro`}
        description={`View shared portfolio with ${portfolio?.holdings?.length || 0} holdings`}
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <Badge variant="outline" className="mb-2">
              <Share2 className="h-3 w-3 mr-1" />
              Shared Portfolio
            </Badge>
            <h1 className="text-3xl font-bold text-gray-900">{portfolio?.name}</h1>
            {portfolio?.description && (
              <p className="text-gray-600 mt-2">{portfolio.description}</p>
            )}
            {badges.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {badges.map((b) => (
                  <Badge key={b.label} className={b.className}>{b.label}</Badge>
                ))}
              </div>
            )}
          </div>
          <Button onClick={handleCopy} disabled={copying} className="gap-2">
            <Copy className="h-4 w-4" />
            {copying ? "Copying..." : "Copy Portfolio"}
          </Button>
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
          {portfolio?.owner && (
            <span className="flex items-center gap-1">
              <User className="h-4 w-4" />
              {portfolio.owner.username || "Anonymous"}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Briefcase className="h-4 w-4" />
            {portfolio?.holdings?.length || 0} holdings
          </span>
          {portfolio?.created_at && (
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {new Date(portfolio.created_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Value</p>
                <p className="text-2xl font-bold">${totalValue.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Return</p>
                <p className={`text-2xl font-bold ${totalReturn >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {totalReturn >= 0 ? "+" : ""}{totalReturn.toFixed(2)}%
                </p>
              </div>
              <div className={`p-3 rounded-full ${totalReturn >= 0 ? "bg-green-100" : "bg-red-100"}`}>
                {totalReturn >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Holdings</p>
                <p className="text-2xl font-bold">{portfolio?.holdings?.length || 0}</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <PieChart className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocation Chart */}
        {allocationData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie
                      data={allocationData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {allocationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Legend />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Holdings Table */}
        <Card>
          <CardHeader>
            <CardTitle>Holdings</CardTitle>
            <CardDescription>All positions in this portfolio</CardDescription>
          </CardHeader>
          <CardContent>
            {portfolio?.holdings?.length > 0 ? (
              <div className="divide-y max-h-[350px] overflow-y-auto">
                {portfolio.holdings.map((holding, index) => (
                  <div
                    key={holding.symbol || index}
                    className="py-3 flex items-center justify-between"
                  >
                    <div>
                      <p className="font-semibold">{holding.symbol}</p>
                      <p className="text-sm text-gray-500">
                        {holding.shares} shares @ ${holding.avg_cost?.toFixed(2) || "N/A"}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        ${(holding.market_value || 0).toLocaleString()}
                      </p>
                      {holding.gain_loss_percent !== undefined && (
                        <p className={`text-sm ${holding.gain_loss_percent >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {holding.gain_loss_percent >= 0 ? "+" : ""}
                          {holding.gain_loss_percent.toFixed(2)}%
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Briefcase className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <p>No holdings in this portfolio</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* CTA */}
      <div className="mt-8 text-center">
        <p className="text-gray-600 mb-4">Want to track your own investments?</p>
        <Link to="/auth/sign-up">
          <Button size="lg">Get Started Free</Button>
        </Link>
      </div>
    </div>
  );
}
