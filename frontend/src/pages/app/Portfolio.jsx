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

const Portfolio = () => {
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
      if (response.success) setPortfolio(response); else setPortfolio({ success: true, data: [], summary: null });
    } catch (error) {
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

  return (
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Portfolio</h1>
      <div className="table-responsive">
        <table className="min-w-full">
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
    </div>
  );
};

export default Portfolio;