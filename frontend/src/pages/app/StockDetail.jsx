import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Skeleton } from "../../components/ui/skeleton";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { 
  ArrowLeft,
  TrendingUp, 
  TrendingDown,
  Star,
  Bell,
  Plus,
  BarChart3,
  Activity,
  DollarSign,
  Volume2,
  Target,
  Calendar,
  Building,
  Users,
  AlertTriangle,
  ExternalLink
} from "lucide-react";
import { getStock, getRealTimeQuote, addWatchlist, createAlert } from "../../api/client";

const StockDetail = () => {
  const { symbol } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  const [stockData, setStockData] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    const fetchStockData = async () => {
      if (!symbol) return;
      
      try {
        const [stockResponse, realtimeResponse] = await Promise.all([
          getStock(symbol).catch(() => null),
          getRealTimeQuote(symbol).catch(() => null)
        ]);

        if (stockResponse?.success) setStockData(stockResponse.data); else setStockData(null);

        if (realtimeResponse) {
          setRealtimeData(realtimeResponse);
        }
      } catch (error) {
        toast.error("Failed to load stock data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStockData();

    // Set up real-time updates every 30 seconds
    const interval = setInterval(async () => {
      try {
        const realtimeResponse = await getRealTimeQuote(symbol);
        if (realtimeResponse) {
          setRealtimeData(realtimeResponse);
        }
      } catch (error) {
        // Silently fail for real-time updates
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [symbol]);

  const handleAddToWatchlist = async () => {
    try {
      await addWatchlist(symbol, {
        watchlist_name: "My Watchlist",
        notes: `Added ${stockData.company_name} from stock detail page`
      });
      toast.success(`${symbol} added to watchlist`);
    } catch (error) {
      toast.error(`Failed to add ${symbol} to watchlist`);
    }
  };

  const handleCreateAlert = async () => {
    try {
      await createAlert({ ticker: symbol, target_price: stockData.current_price * 1.05, condition: "above" });
      toast.success("Price alert created successfully");
    } catch (error) {
      toast.error("Failed to create price alert");
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatMarketCap = (value) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  const formatVolume = (value) => {
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
    return value.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-20" />
            <Skeleton className="h-8 w-48" />
          </div>
          
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <Skeleton className="h-8 w-32" />
                  <Skeleton className="h-6 w-48" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-64 w-full" />
                </CardContent>
              </Card>
            </div>
            <div>
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-24" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="flex justify-between">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-16" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Stock data not found for symbol "{symbol}". Please check the symbol and try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentData = (realtimeData || stockData) || {};
  const isPositive = (currentData.change_percent ?? 0) >= 0;

  return (
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">{symbol} Details</h1>
      <div className="table-responsive">
        {/* details content */}
      </div>
    </div>
  );
};

export default StockDetail;