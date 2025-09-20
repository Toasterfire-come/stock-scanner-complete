import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { RefreshCw, TrendingUp, TrendingDown } from "lucide-react";
import { toast } from "sonner";
import { listStocks } from "../../api/client";

const MarketHeatmap = () => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState("change_percent");
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState("");

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
    setError("");
    try {
      const data = await listStocks({ limit: 50 });
      const rows = data?.data || [];
      setHeatmapData(Array.isArray(rows) ? rows : []);
      setLastUpdated(new Date());
      if (!data?.success) {
        setError("Stocks API returned non-success response");
      }
    } catch (error) {
      setError("Failed to fetch heatmap data");
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
    const v = Number(value);
    if (metric === "change_percent") return Number.isFinite(v) ? v : 0;
    const values = data.map(item => Number(item[metric] || 0));
    const max = Math.max(...values);
    const min = Math.min(...values);
    if (!Number.isFinite(max) || !Number.isFinite(min) || max === min) return 0;
    return (v - min) / (max - min);
  };

  const formatValue = (value, metric) => {
    const v = Number(value);
    if (metric === "change_percent") return `${v >= 0 ? '+' : ''}${(Number.isFinite(v) ? v : 0).toFixed(2)}%`;
    if (metric === "volume") return (Number.isFinite(v) ? (v / 1e6).toFixed(1) : 0) + "M";
    if (metric === "market_cap") return "$" + (Number.isFinite(v) ? (v / 1e9).toFixed(1) : 0) + "B";
    return (Number.isFinite(v) ? v : 0).toString();
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
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Market Heatmap</h1>
      {/* heatmap content */}
    </div>
  );
};

export default MarketHeatmap;