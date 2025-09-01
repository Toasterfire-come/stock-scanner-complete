import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { RefreshCw, TrendingUp, TrendingDown } from "lucide-react";
import { toast } from "sonner";

const MarketHeatmap = () => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState("change_percent");
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const metrics = [
    { value: "change_percent", label: "Price Change %" },
    { value: "volume", label: "Volume" },
    { value: "market_cap", label: "Market Cap" }
  ];

  useEffect(() => {
    fetchHeatmapData();
  }, [selectedMetric]);

  const fetchHeatmapData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/stocks/?limit=50`);
      const data = await response.json();
      
      if (data.success) {
        setHeatmapData(data.data);
        setLastUpdated(new Date());
      }
    } catch (error) {
      toast.error("Failed to fetch heatmap data");
    } finally {
      setIsLoading(false);
    }
  };

  const getColor = (value, metric) => {
    if (metric === "change_percent") {
      if (value > 5) return "bg-green-600 text-white";
      if (value > 2) return "bg-green-500 text-white";
      if (value > 0) return "bg-green-200 text-green-800";
      if (value > -2) return "bg-red-200 text-red-800";
      if (value > -5) return "bg-red-500 text-white";
      return "bg-red-600 text-white";
    }
    
    // For volume and market cap, use blue scale
    if (value > 0.8) return "bg-blue-600 text-white";
    if (value > 0.6) return "bg-blue-500 text-white";
    if (value > 0.4) return "bg-blue-200 text-blue-800";
    return "bg-gray-200 text-gray-800";
  };

  const normalizeValue = (value, metric, data) => {
    if (metric === "change_percent") return value;
    
    const values = data.map(item => item[metric]);
    const max = Math.max(...values);
    const min = Math.min(...values);
    return (value - min) / (max - min);
  };

  const formatValue = (value, metric) => {
    if (metric === "change_percent") return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    if (metric === "volume") return (value / 1e6).toFixed(1) + "M";
    if (metric === "market_cap") return "$" + (value / 1e9).toFixed(1) + "B";
    return value.toString();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Market Heatmap</h1>
          <p className="text-gray-600 mt-2">Visual representation of market performance</p>
        </div>
        <div className="flex items-center gap-4">
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {metrics.map((metric) => (
                <SelectItem key={metric.value} value={metric.value}>
                  {metric.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchHeatmapData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Market Overview
              <Badge variant="outline">
                {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-auto-fit gap-2" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              {heatmapData.map((stock) => {
                const value = stock[selectedMetric];
                const normalizedValue = normalizeValue(value, selectedMetric, heatmapData);
                const colorClass = getColor(selectedMetric === "change_percent" ? value : normalizedValue, selectedMetric);
                
                return (
                  <div
                    key={stock.ticker}
                    className={`p-3 rounded-lg cursor-pointer hover:opacity-80 transition-opacity ${colorClass}`}
                    title={`${stock.company_name} - ${formatValue(value, selectedMetric)}`}
                  >
                    <div className="font-semibold text-sm">{stock.ticker}</div>
                    <div className="text-xs opacity-90">{formatValue(value, selectedMetric)}</div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Market Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {heatmapData.filter(s => s.change_percent > 0).length}
                </div>
                <div className="text-sm text-gray-600 flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Gainers
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {heatmapData.filter(s => s.change_percent < 0).length}
                </div>
                <div className="text-sm text-gray-600 flex items-center justify-center">
                  <TrendingDown className="h-4 w-4 mr-1" />
                  Losers
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {heatmapData.filter(s => s.change_percent === 0).length}
                </div>
                <div className="text-sm text-gray-600">Unchanged</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {(heatmapData.reduce((sum, s) => sum + s.volume, 0) / 1e9).toFixed(1)}B
                </div>
                <div className="text-sm text-gray-600">Total Volume</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MarketHeatmap;