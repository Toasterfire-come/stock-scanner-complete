import React, { useState, useEffect } from "react";
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
  BarChart3,
  Target,
  Trash2,
  Edit,
  RefreshCw,
  Download,
  Calculator
} from "lucide-react";
import { getPortfolio, addPortfolio, deletePortfolio } from "../../api/client";

const Portfolio = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newHolding, setNewHolding] = useState({
    symbol: "",
    shares: "",
    avg_cost: "",
    portfolio_name: "My Portfolio"
  });

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await getPortfolio();
        if (response.success) {
          setPortfolio(response);
        } else {
          // Mock portfolio data
          setPortfolio({
            success: true,
            data: [
              {
                id: "1",
                symbol: "AAPL",
                shares: 50,
                avg_cost: 150.00,
                current_price: 175.25,
                total_value: 8762.50,
                gain_loss: 1262.50,
                gain_loss_percent: 16.83,
                portfolio_name: "My Portfolio",
                added_date: "2024-02-15T10:30:00Z"
              },
              {
                id: "2",
                symbol: "MSFT",
                shares: 25,
                avg_cost: 380.00,
                current_price: 415.67,
                total_value: 10391.75,
                gain_loss: 891.75,
                gain_loss_percent: 9.39,
                portfolio_name: "My Portfolio",
                added_date: "2024-02-20T14:20:00Z"
              },
              {
                id: "3",
                symbol: "GOOGL",
                shares: 15,
                avg_cost: 140.00,
                current_price: 142.50,
                total_value: 2137.50,
                gain_loss: 37.50,
                gain_loss_percent: 1.79,
                portfolio_name: "My Portfolio",
                added_date: "2024-03-01T09:15:00Z"
              }
            ],
            summary: {
              total_value: 21291.75,
              total_gain_loss: 2191.75,
              total_gain_loss_percent: 11.48,
              total_holdings: 3
            }
          });
        }
      } catch (error) {
        toast.error("Failed to load portfolio");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPortfolio();
  }, []);

  const handleAddHolding = async (e) => {
    e.preventDefault();
    setIsAdding(true);

    try {
      const response = await addPortfolio({
        symbol: newHolding.symbol.toUpperCase(),
        shares: parseFloat(newHolding.shares),
        avg_cost: parseFloat(newHolding.avg_cost),
        portfolio_name: newHolding.portfolio_name
      });

      if (response.success) {
        toast.success(`${newHolding.symbol.toUpperCase()} added to portfolio`);
        setIsAddModalOpen(false);
        setNewHolding({ symbol: "", shares: "", avg_cost: "", portfolio_name: "My Portfolio" });
        
        // Refresh portfolio data
        const updatedPortfolio = await getPortfolio();
        if (updatedPortfolio.success) {
          setPortfolio(updatedPortfolio);
        }
      } else {
        toast.error("Failed to add holding to portfolio");
      }
    } catch (error) {
      toast.error("Failed to add holding to portfolio");
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteHolding = async (id, symbol) => {
    try {
      const response = await deletePortfolio(id);
      if (response.success) {
        toast.success(`${symbol} removed from portfolio`);
        setPortfolio(prev => ({
          ...prev,
          data: prev.data.filter(holding => holding.id !== id),
          summary: {
            ...prev.summary,
            total_holdings: prev.summary.total_holdings - 1
          }
        }));
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
      <div className="container mx-auto px-4 py-8 max-w-6xl">
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

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
            <p className="text-gray-600 mt-2">
              Track your investments and performance
            </p>
          </div>
          
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Holding
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Holding</DialogTitle>
                <DialogDescription>
                  Add a stock position to your portfolio
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleAddHolding} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="symbol">Stock Symbol</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g., AAPL"
                    value={newHolding.symbol}
                    onChange={(e) => setNewHolding(prev => ({ ...prev, symbol: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="shares">Shares</Label>
                    <Input
                      id="shares"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={newHolding.shares}
                      onChange={(e) => setNewHolding(prev => ({ ...prev, shares: e.target.value }))}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="avg_cost">Average Cost</Label>
                    <Input
                      id="avg_cost"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={newHolding.avg_cost}
                      onChange={(e) => setNewHolding(prev => ({ ...prev, avg_cost: e.target.value }))}
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="portfolio_name">Portfolio Name</Label>
                  <Input
                    id="portfolio_name"
                    placeholder="My Portfolio"
                    value={newHolding.portfolio_name}
                    onChange={(e) => setNewHolding(prev => ({ ...prev, portfolio_name: e.target.value }))}
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setIsAddModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isAdding}>
                    {isAdding ? "Adding..." : "Add Holding"}
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
                    <p className="text-2xl font-bold text-blue-600">
                      {formatCurrency(portfolio.summary.total_value)}
                    </p>
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
                    <p className={`text-2xl font-bold ${
                      portfolio.summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(portfolio.summary.total_gain_loss)}
                    </p>
                  </div>
                  {portfolio.summary.total_gain_loss >= 0 ? (
                    <TrendingUp className="h-8 w-8 text-green-500" />
                  ) : (
                    <TrendingDown className="h-8 w-8 text-red-500" />
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Return</p>
                    <p className={`text-2xl font-bold ${
                      portfolio.summary.total_gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(portfolio.summary.total_gain_loss_percent)}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Holdings</p>
                    <p className="text-2xl font-bold">
                      {portfolio.summary.total_holdings}
                    </p>
                  </div>
                  <PieChart className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Holdings Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Your Holdings
              </CardTitle>
              <CardDescription>
                Track your stock positions and performance
              </CardDescription>
            </div>
            
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {portfolio?.data?.length > 0 ? (
              <>
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
                                <span className="font-bold text-blue-600 text-sm">
                                  {holding.symbol.substring(0, 2)}
                                </span>
                              </div>
                              <div>
                                <div className="font-semibold">{holding.symbol}</div>
                                <div className="text-sm text-gray-500">
                                  Added {new Date(holding.added_date).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="p-4 text-right font-medium">
                            {holding.shares.toLocaleString()}
                          </td>
                          <td className="p-4 text-right">
                            {formatCurrency(holding.avg_cost)}
                          </td>
                          <td className="p-4 text-right font-medium">
                            {formatCurrency(holding.current_price)}
                          </td>
                          <td className="p-4 text-right font-semibold">
                            {formatCurrency(holding.total_value)}
                          </td>
                          <td className={`p-4 text-right font-medium ${
                            holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatCurrency(holding.gain_loss)}
                          </td>
                          <td className={`p-4 text-right font-medium ${
                            holding.gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            <div className="flex items-center justify-end">
                              {holding.gain_loss_percent >= 0 ? (
                                <TrendingUp className="h-3 w-3 mr-1" />
                              ) : (
                                <TrendingDown className="h-3 w-3 mr-1" />
                              )}
                              {formatPercentage(holding.gain_loss_percent)}
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center justify-center space-x-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                title="Edit Holding"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDeleteHolding(holding.id, holding.symbol)}
                                title="Remove Holding"
                                className="text-red-600 hover:text-red-700"
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

                {/* Mobile Card View */}
                <div className="lg:hidden space-y-4">
                  {portfolio.data.map((holding) => (
                    <Card key={holding.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                              <span className="font-bold text-blue-600">
                                {holding.symbol.substring(0, 2)}
                              </span>
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{holding.symbol}</div>
                              <div className="text-sm text-gray-500">
                                {holding.shares} shares
                              </div>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="font-semibold text-lg">
                              {formatCurrency(holding.total_value)}
                            </div>
                            <div className={`text-sm font-medium ${
                              holding.gain_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {formatPercentage(holding.gain_loss_percent)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <div className="text-gray-600">Avg Cost</div>
                            <div className="font-medium">{formatCurrency(holding.avg_cost)}</div>
                          </div>
                          <div>
                            <div className="text-gray-600">Current Price</div>
                            <div className="font-medium">{formatCurrency(holding.current_price)}</div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between mt-4">
                          <div className={`text-sm font-medium ${
                            holding.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            P&L: {formatCurrency(holding.gain_loss)}
                          </div>
                          <div className="flex space-x-2">
                            <Button size="sm" variant="ghost">
                              <Edit className="h-4 w-4" />
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
              </>
            ) : (
              <div className="text-center py-12">
                <PieChart className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Holdings Yet</h3>
                <p className="text-gray-600 mb-4">
                  Add your first stock position to start tracking your portfolio performance.
                </p>
                <Button onClick={() => setIsAddModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Your First Holding
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Portfolio Analytics */}
        {portfolio?.data?.length > 0 && (
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Allocation by Position</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {portfolio.data.map((holding) => {
                    const percentage = (holding.total_value / portfolio.summary.total_value) * 100;
                    return (
                      <div key={holding.id}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{holding.symbol}</span>
                          <span className="text-sm text-gray-600">
                            {percentage.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Best Performer</span>
                    <span className="font-medium text-green-600">
                      {portfolio.data.reduce((best, holding) => 
                        holding.gain_loss_percent > best.gain_loss_percent ? holding : best
                      ).symbol} ({formatPercentage(
                        portfolio.data.reduce((best, holding) => 
                          holding.gain_loss_percent > best.gain_loss_percent ? holding : best
                        ).gain_loss_percent
                      )})
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Worst Performer</span>
                    <span className="font-medium text-red-600">
                      {portfolio.data.reduce((worst, holding) => 
                        holding.gain_loss_percent < worst.gain_loss_percent ? holding : worst
                      ).symbol} ({formatPercentage(
                        portfolio.data.reduce((worst, holding) => 
                          holding.gain_loss_percent < worst.gain_loss_percent ? holding : worst
                        ).gain_loss_percent
                      )})
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Largest Position</span>
                    <span className="font-medium">
                      {portfolio.data.reduce((largest, holding) => 
                        holding.total_value > largest.total_value ? holding : largest
                      ).symbol} ({formatCurrency(
                        portfolio.data.reduce((largest, holding) => 
                          holding.total_value > largest.total_value ? holding : largest
                        ).total_value
                      )})
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Total Cost Basis</span>
                    <span className="font-medium">
                      {formatCurrency(
                        portfolio.data.reduce((total, holding) => 
                          total + (holding.shares * holding.avg_cost), 0
                        )
                      )}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;