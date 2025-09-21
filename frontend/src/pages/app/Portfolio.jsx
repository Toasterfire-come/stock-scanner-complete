import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../../components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { toast } from "sonner";
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  PieChart, 
  DollarSign,
  Trash2,
  Edit,
  Eye,
  BarChart3,
  Download,
  Calendar,
  Target,
  AlertCircle
} from "lucide-react";
import { 
  getPortfolio, 
  addPortfolio, 
  deletePortfolio,
  getPortfolioAnalytics,
  getPortfolioSectorAllocation,
  getPortfolioDividendTracking,
  exportPortfolioCSV
} from "../../api/client";

const Portfolio = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [sectorAllocation, setSectorAllocation] = useState([]);
  const [dividendData, setDividendData] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newHolding, setNewHolding] = useState({
    symbol: "",
    shares: "",
    avg_cost: "",
    portfolio_name: "My Portfolio"
  });

  useEffect(() => {
    fetchAllPortfolioData();
  }, []);

  const fetchAllPortfolioData = async () => {
    setIsLoading(true);
    try {
      // Fetch all portfolio data in parallel
      const [
        portfolioResponse,
        analyticsResponse,
        sectorResponse,
        dividendResponse
      ] = await Promise.all([
        getPortfolio().catch(() => ({ success: true, data: [], summary: { total_value: 0, total_gain_loss: 0, total_gain_loss_percent: 0, total_holdings: 0 } })),
        getPortfolioAnalytics().catch(() => null),
        getPortfolioSectorAllocation().catch(() => []),
        getPortfolioDividendTracking().catch(() => null)
      ]);

      setPortfolio(portfolioResponse);
      setAnalytics(analyticsResponse);
      setSectorAllocation(sectorResponse);
      setDividendData(dividendResponse);
    } catch (error) {
      console.error("Failed to load portfolio data:", error);
      toast.error("Failed to load portfolio data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    
    if (!newHolding.symbol || !newHolding.shares || !newHolding.avg_cost) {
      toast.error("Please fill in all required fields");
      return;
    }

    try {
      const response = await addPortfolio({
        symbol: newHolding.symbol.toUpperCase(),
        shares: parseFloat(newHolding.shares),
        avg_cost: parseFloat(newHolding.avg_cost),
        portfolio_name: newHolding.portfolio_name
      });

      if (response && response.success) {
        toast.success("Stock added to portfolio successfully");
        setIsAddModalOpen(false);
        setNewHolding({
          symbol: "",
          shares: "",
          avg_cost: "",
          portfolio_name: "My Portfolio"
        });
        // Refresh all portfolio data
        fetchAllPortfolioData();
      } else {
        throw new Error(response?.message || 'Failed to add stock');
      }
    } catch (error) {
      console.error("Failed to add stock:", error);
      toast.error(error.message || "Failed to add stock to portfolio");
    }
  };

  const handleDeleteStock = async (holdingId) => {
    if (!window.confirm("Are you sure you want to remove this stock from your portfolio?")) {
      return;
    }

    try {
      const response = await deletePortfolio(holdingId);
      if (response && response.success) {
        toast.success("Stock removed from portfolio");
        fetchAllPortfolioData();
      } else {
        throw new Error(response?.message || 'Failed to delete stock');
      }
    } catch (error) {
      console.error("Failed to delete stock:", error);
      toast.error(error.message || "Failed to remove stock from portfolio");
    }
  };

  const handleExportPortfolio = async () => {
    try {
      const csvData = await exportPortfolioCSV();
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("Portfolio exported successfully");
    } catch (error) {
      console.error("Failed to export portfolio:", error);
      toast.error("Failed to export portfolio");
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '$0.00';
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0.00%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-96" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-8 w-32 mb-2" />
                <Skeleton className="h-3 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const portfolioSummary = analytics || portfolio?.summary || {
    total_value: 0,
    total_gain_loss: 0,
    total_gain_loss_percent: 0,
    day_change: 0,
    day_change_percent: 0
  };

  const holdings = portfolio?.data || [];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
          <p className="text-gray-600">Track and analyze your investments</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleExportPortfolio} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Stock
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Stock to Portfolio</DialogTitle>
                <DialogDescription>
                  Enter the stock details to add to your portfolio
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddStock} className="space-y-4">
                <div>
                  <Label htmlFor="symbol">Stock Symbol *</Label>
                  <Input
                    id="symbol"
                    value={newHolding.symbol}
                    onChange={(e) => setNewHolding({...newHolding, symbol: e.target.value})}
                    placeholder="AAPL"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="shares">Number of Shares *</Label>
                  <Input
                    id="shares"
                    type="number"
                    step="0.001"
                    value={newHolding.shares}
                    onChange={(e) => setNewHolding({...newHolding, shares: e.target.value})}
                    placeholder="100"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="avg_cost">Average Cost per Share *</Label>
                  <Input
                    id="avg_cost"
                    type="number"
                    step="0.01"
                    value={newHolding.avg_cost}
                    onChange={(e) => setNewHolding({...newHolding, avg_cost: e.target.value})}
                    placeholder="150.00"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="portfolio_name">Portfolio Name</Label>
                  <Input
                    id="portfolio_name"
                    value={newHolding.portfolio_name}
                    onChange={(e) => setNewHolding({...newHolding, portfolio_name: e.target.value})}
                    placeholder="My Portfolio"
                  />
                </div>
                <Button type="submit" className="w-full">
                  Add to Portfolio
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-2xl font-bold">{formatCurrency(portfolioSummary.total_value)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className={`bg-gradient-to-r ${portfolioSummary.total_gain_loss >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Gain/Loss</p>
                <p className={`text-2xl font-bold ${portfolioSummary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(portfolioSummary.total_gain_loss)}
                </p>
                <p className={`text-sm ${portfolioSummary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(portfolioSummary.total_gain_loss_percent)}
                </p>
              </div>
              {portfolioSummary.total_gain_loss >= 0 ? 
                <TrendingUp className="h-8 w-8 text-green-600" /> : 
                <TrendingDown className="h-8 w-8 text-red-600" />
              }
            </div>
          </CardContent>
        </Card>

        <Card className={`bg-gradient-to-r ${portfolioSummary.day_change >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Today's Change</p>
                <p className={`text-2xl font-bold ${portfolioSummary.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(portfolioSummary.day_change || 0)}
                </p>
                <p className={`text-sm ${portfolioSummary.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(portfolioSummary.day_change_percent || 0)}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-50 to-purple-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Holdings</p>
                <p className="text-2xl font-bold">{holdings.length}</p>
                <p className="text-sm text-gray-600">
                  {dividendData?.annual_income ? formatCurrency(dividendData.annual_income) + ' dividends' : 'Stocks tracked'}
                </p>
              </div>
              <PieChart className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different views */}
      <Tabs defaultValue="holdings" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="holdings">Holdings</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="sectors">Sectors</TabsTrigger>
          <TabsTrigger value="dividends">Dividends</TabsTrigger>
        </TabsList>

        {/* Holdings Tab */}
        <TabsContent value="holdings">
          <Card>
            <CardHeader>
              <CardTitle>Your Holdings</CardTitle>
              <CardDescription>
                Manage your portfolio positions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {holdings.length === 0 ? (
                <div className="text-center py-12">
                  <PieChart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Holdings Yet</h3>
                  <p className="text-gray-600 mb-6">Start building your portfolio by adding your first stock position.</p>
                  <Button onClick={() => setIsAddModalOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Stock
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {holdings.map((holding, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-4">
                          <div>
                            <h3 className="font-semibold text-lg">{holding.symbol}</h3>
                            <p className="text-sm text-gray-600">{holding.name || 'Company Name'}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">{holding.shares} shares</p>
                            <p className="text-sm text-gray-600">@ {formatCurrency(holding.avg_cost)}</p>
                          </div>
                        </div>
                      </div>
                      <div className="text-right mr-4">
                        <p className="font-semibold">{formatCurrency(holding.current_value || 0)}</p>
                        <p className={`text-sm ${(holding.gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(holding.gain_loss || 0)} ({formatPercent(holding.gain_loss_percent || 0)})
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteStock(holding.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Performance Analytics</CardTitle>
                <CardDescription>Detailed analysis of your portfolio performance</CardDescription>
              </CardHeader>
              <CardContent>
                {analytics ? (
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Risk Metrics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Beta:</span>
                          <span className="font-medium">{analytics.beta?.toFixed(2) || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sharpe Ratio:</span>
                          <span className="font-medium">{analytics.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Volatility:</span>
                          <span className="font-medium">{analytics.volatility ? `${(analytics.volatility * 100).toFixed(1)}%` : 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3">Returns</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">1 Month:</span>
                          <span className={`font-medium ${(analytics.returns_1m || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(analytics.returns_1m || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">3 Months:</span>
                          <span className={`font-medium ${(analytics.returns_3m || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(analytics.returns_3m || 0)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">YTD:</span>
                          <span className={`font-medium ${(analytics.returns_ytd || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(analytics.returns_ytd || 0)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Add some holdings to see detailed analytics</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Sectors Tab */}
        <TabsContent value="sectors">
          <Card>
            <CardHeader>
              <CardTitle>Sector Allocation</CardTitle>
              <CardDescription>Your portfolio diversification across sectors</CardDescription>
            </CardHeader>
            <CardContent>
              {sectorAllocation.length > 0 ? (
                <div className="space-y-4">
                  {sectorAllocation.map((sector, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{sector.sector_name}</h4>
                        <p className="text-sm text-gray-600">{sector.stocks_count} stocks</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{formatCurrency(sector.value)}</p>
                        <p className="text-sm text-gray-600">{sector.percentage?.toFixed(1)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Add holdings to see sector allocation</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Dividends Tab */}
        <TabsContent value="dividends">
          <Card>
            <CardHeader>
              <CardTitle>Dividend Tracking</CardTitle>
              <CardDescription>Monitor your dividend income and projections</CardDescription>
            </CardHeader>
            <CardContent>
              {dividendData ? (
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Income Summary</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Annual Income:</span>
                        <span className="font-medium text-green-600">{formatCurrency(dividendData.annual_income)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Quarterly:</span>
                        <span className="font-medium">{formatCurrency(dividendData.quarterly_income)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Yield:</span>
                        <span className="font-medium">{dividendData.average_yield?.toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-3">Next Payments</h4>
                    {dividendData.upcoming_payments?.slice(0, 3).map((payment, index) => (
                      <div key={index} className="flex justify-between items-center py-2">
                        <div>
                          <span className="font-medium">{payment.symbol}</span>
                          <span className="text-sm text-gray-600 ml-2">{payment.ex_date}</span>
                        </div>
                        <span className="font-medium text-green-600">{formatCurrency(payment.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Add dividend-paying stocks to track income</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Portfolio;