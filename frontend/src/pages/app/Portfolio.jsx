import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../../components/ui/dialog";
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
  BarChart3
} from "lucide-react";
import { getPortfolio, addPortfolio, deletePortfolio } from "../../api/client";
import { useAuth } from "../../context/SecureAuthContext";

const Portfolio = () => {
  const { isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newHolding, setNewHolding] = useState({
    symbol: "",
    shares: "",
    avg_cost: "",
    portfolio_name: "My Portfolio"
  });

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const response = await getPortfolio();
      if (response && response.success) {
        setPortfolio(response);
      } else {
        setPortfolio({ success: true, data: [], summary: { total_value: 0, total_gain_loss: 0, total_gain_loss_percent: 0, total_holdings: 0 } });
      }
    } catch (error) {
      setPortfolio({ success: true, data: [], summary: { total_value: 0, total_gain_loss: 0, total_gain_loss_percent: 0, total_holdings: 0 } });
      toast.error("Failed to load portfolio");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddHolding = async (e) => {
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

      if (response.success) {
        toast.success(`${newHolding.symbol.toUpperCase()} added to portfolio`);
        setNewHolding({ symbol: "", shares: "", avg_cost: "", portfolio_name: "My Portfolio" });
        setIsAddModalOpen(false);
        fetchPortfolio();
      } else {
        toast.error(response.message || "Failed to add holding");
      }
    } catch (error) {
      toast.error("Failed to add holding to portfolio");
    }
  };

  const handleDeleteHolding = async (id, symbol) => {
    if (!confirm(`Are you sure you want to remove ${symbol} from your portfolio?`)) return;
    
    try {
      const response = await deletePortfolio(id);
      if (response.success) {
        toast.success(`${symbol} removed from portfolio`);
        fetchPortfolio();
      } else {
        toast.error("Failed to remove holding");
      }
    } catch (error) {
      toast.error("Failed to remove holding");
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Card>
          <CardHeader>
            <CardTitle>Portfolio</CardTitle>
            <CardDescription>Sign in to track your holdings and performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-gray-600">You need to be signed in to view and manage your portfolio.</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
            <p className="text-gray-600 mt-2">Track your investments and performance</p>
          </div>
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Holding
              </Button>
            </DialogTrigger>
            <DialogContent aria-describedby="portfolio-dialog-desc">
              <DialogTitle className="sr-only">Add Holding</DialogTitle>
              <DialogDescription id="portfolio-dialog-desc" className="sr-only">Add or edit a portfolio holding</DialogDescription>
              <DialogHeader>
                <DialogTitle>Add New Holding</DialogTitle>
                <DialogDescription>
                  Add a stock to your portfolio to track its performance
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddHolding} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="symbol">Stock Symbol</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g. AAPL"
                    value={newHolding.symbol}
                    onChange={(e) => setNewHolding({...newHolding, symbol: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="shares">Number of Shares</Label>
                  <Input
                    id="shares"
                    type="number"
                    step="0.01"
                    placeholder="e.g. 100"
                    value={newHolding.shares}
                    onChange={(e) => setNewHolding({...newHolding, shares: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="avg_cost">Average Cost per Share</Label>
                  <Input
                    id="avg_cost"
                    type="number"
                    step="0.01"
                    placeholder="e.g. 150.25"
                    value={newHolding.avg_cost}
                    onChange={(e) => setNewHolding({...newHolding, avg_cost: e.target.value})}
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">Add Holding</Button>
                  <Button type="button" variant="outline" onClick={() => setIsAddModalOpen(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Portfolio Summary */}
        {portfolio?.summary && (
          <div className="grid md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Value</p>
                    <p className="text-2xl font-bold">{formatCurrency(portfolio.summary.total_value)}</p>
                  </div>
                  <DollarSign className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total P&L</p>
                    <div className="flex items-center">
                      <p className={`text-2xl font-bold ${portfolio.summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(portfolio.summary.total_gain_loss)}
                      </p>
                      {portfolio.summary.total_gain_loss >= 0 ? 
                        <TrendingUp className="h-5 w-5 text-green-500 ml-2" /> : 
                        <TrendingDown className="h-5 w-5 text-red-500 ml-2" />
                      }
                    </div>
                  </div>
                  <BarChart3 className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Return</p>
                    <p className={`text-2xl font-bold ${portfolio.summary.total_gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercentage(portfolio.summary.total_gain_loss_percent)}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Holdings</p>
                    <p className="text-2xl font-bold">{portfolio.summary.total_holdings}</p>
                  </div>
                  <PieChart className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Holdings List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Holdings</CardTitle>
            <CardDescription>
              Detailed view of your portfolio positions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {portfolio?.data?.length > 0 ? (
              <div className="space-y-4">
                {/* Desktop Table */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-left p-4 font-medium">Symbol</th>
                        <th className="text-right p-4 font-medium">Shares</th>
                        <th className="text-right p-4 font-medium">Avg Cost</th>
                        <th className="text-right p-4 font-medium">Current Price</th>
                        <th className="text-right p-4 font-medium">Total Value</th>
                        <th className="text-right p-4 font-medium">P&L</th>
                        <th className="text-right p-4 font-medium">% Return</th>
                        <th className="text-center p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.data.map((holding) => (
                        <tr key={holding.id} className="border-b hover:bg-gray-50">
                          <td className="p-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <span className="font-bold text-blue-600 text-sm">{holding.symbol.substring(0, 2)}</span>
                              </div>
                              <div>
                                <Link to={`/app/stocks/${holding.symbol}`} className="font-semibold text-blue-600 hover:underline">
                                  {holding.symbol}
                                </Link>
                              </div>
                            </div>
                          </td>
                          <td className="p-4 text-right">{holding.shares}</td>
                          <td className="p-4 text-right">{formatCurrency(holding.avg_cost)}</td>
                          <td className="p-4 text-right font-medium">{formatCurrency(holding.current_price)}</td>
                          <td className="p-4 text-right font-medium">{formatCurrency(holding.total_value)}</td>
                          <td className={`p-4 text-right font-medium ${holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(holding.gain_loss)}
                          </td>
                          <td className={`p-4 text-right font-medium ${holding.gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            <div className="flex items-center justify-end">
                              {holding.gain_loss_percent >= 0 ? 
                                <TrendingUp className="h-3 w-3 mr-1" /> : 
                                <TrendingDown className="h-3 w-3 mr-1" />
                              }
                              {formatPercentage(holding.gain_loss_percent)}
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center justify-center space-x-2">
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                asChild
                                title="View Details"
                              >
                                <Link to={`/app/stocks/${holding.symbol}`}>
                                  <Eye className="h-4 w-4" />
                                </Link>
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                onClick={() => handleDeleteHolding(holding.id, holding.symbol)}
                                className="text-red-600 hover:text-red-700"
                                title="Remove Holding"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Cards */}
                <div className="lg:hidden space-y-4">
                  {portfolio.data.map((holding) => (
                    <Card key={holding.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                              <span className="font-bold text-blue-600">{holding.symbol.substring(0, 2)}</span>
                            </div>
                            <div>
                              <Link to={`/app/stocks/${holding.symbol}`} className="font-semibold text-blue-600 hover:underline">
                                {holding.symbol}
                              </Link>
                              <div className="text-sm text-gray-600">{holding.shares} shares</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-lg">{formatCurrency(holding.total_value)}</div>
                            <div className={`text-sm font-medium ${holding.gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'} flex items-center justify-end`}>
                              {holding.gain_loss_percent >= 0 ? 
                                <TrendingUp className="h-3 w-3 mr-1" /> : 
                                <TrendingDown className="h-3 w-3 mr-1" />
                              }
                              {formatPercentage(holding.gain_loss_percent)}
                            </div>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="text-gray-500">Avg Cost</div>
                            <div className="font-medium">{formatCurrency(holding.avg_cost)}</div>
                          </div>
                          <div>
                            <div className="text-gray-500">Current Price</div>
                            <div className="font-medium">{formatCurrency(holding.current_price)}</div>
                          </div>
                          <div>
                            <div className="text-gray-500">P&L</div>
                            <div className={`font-medium ${holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(holding.gain_loss)}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button size="sm" variant="ghost" asChild>
                              <Link to={`/app/stocks/${holding.symbol}`}>
                                <Eye className="h-4 w-4" />
                              </Link>
                            </Button>
                            <Button 
                              size="sm" 
                              variant="ghost" 
                              onClick={() => handleDeleteHolding(holding.id, holding.symbol)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <PieChart className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No holdings yet</h3>
                <p className="text-gray-600 mb-4">
                  Start tracking your investments by adding your first stock holding
                </p>
                <Button onClick={() => setIsAddModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Your First Holding
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Portfolio;