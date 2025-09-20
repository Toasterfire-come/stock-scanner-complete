import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Search, Download, Filter, TrendingUp, TrendingDown, Calendar, Clock } from "lucide-react";
import { toast } from "sonner";
import { getAlertHistory } from "../../api/client";

const AlertHistory = () => {
  const [alertHistory, setAlertHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  const statusOptions = [
    { value: "all", label: "All Status" },
    { value: "triggered", label: "Triggered" },
    { value: "expired", label: "Expired" },
    { value: "cancelled", label: "Cancelled" }
  ];

  const dateOptions = [
    { value: "all", label: "All Time" },
    { value: "today", label: "Today" },
    { value: "week", label: "This Week" },
    { value: "month", label: "This Month" },
    { value: "quarter", label: "This Quarter" }
  ];

  useEffect(() => {
    fetchAlertHistory();
  }, []);

  useEffect(() => {
    filterHistory();
  }, [alertHistory, searchTerm, statusFilter, dateFilter]);

  const fetchAlertHistory = async () => {
    setIsLoading(true);
    try {
      const res = await getAlertHistory();
      const items = Array.isArray(res?.data) ? res.data : Array.isArray(res) ? res : [];
      setAlertHistory(items);
    } catch (error) {
      toast.error("Failed to fetch alert history");
      setAlertHistory([]);
    } finally { setIsLoading(false); }
  };

  const filterHistory = () => {
    let filtered = [...alertHistory];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(alert =>
        alert.ticker.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(alert => alert.status === statusFilter);
    }

    // Date filter
    if (dateFilter !== "all") {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      filtered = filtered.filter(alert => {
        const alertDate = new Date(alert.createdAt);
        
        switch (dateFilter) {
          case "today":
            return alertDate >= today;
          case "week":
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            return alertDate >= weekAgo;
          case "month":
            const monthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
            return alertDate >= monthAgo;
          case "quarter":
            const quarterAgo = new Date(today.getFullYear(), today.getMonth() - 3, today.getDate());
            return alertDate >= quarterAgo;
          default:
            return true;
        }
      });
    }

    setFilteredHistory(filtered);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "triggered":
        return "bg-green-100 text-green-800";
      case "expired":
        return "bg-yellow-100 text-yellow-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getConditionIcon = (condition) => {
    return condition === "above" ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    );
  };

  const formatPrice = (price) => price ? `$${price.toFixed(2)}` : 'N/A';
  const formatGain = (gain) => {
    if (gain === null) return 'N/A';
    return `${gain >= 0 ? '+' : ''}$${gain.toFixed(2)}`;
  };

  const exportHistory = () => {
    const csv = [
      "Ticker,Target Price,Trigger Price,Condition,Status,Created At,Triggered/Expired At,Gain/Loss",
      ...filteredHistory.map(alert =>
        `${alert.ticker},${alert.targetPrice},${alert.triggerPrice || 'N/A'},${alert.condition},${alert.status},${new Date(alert.createdAt).toLocaleString()},${alert.triggeredAt ? new Date(alert.triggeredAt).toLocaleString() : (alert.expiredAt ? new Date(alert.expiredAt).toLocaleString() : 'N/A')},${formatGain(alert.gain)}`
      )
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "alert-history.csv";
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success("Alert history exported");
  };

  const getStats = () => {
    const triggered = alertHistory.filter(a => a.status === "triggered");
    const totalGain = triggered.reduce((sum, alert) => sum + (alert.gain || 0), 0);
    const avgGain = triggered.length > 0 ? totalGain / triggered.length : 0;
    
    return {
      total: alertHistory.length,
      triggered: triggered.length,
      expired: alertHistory.filter(a => a.status === "expired").length,
      cancelled: alertHistory.filter(a => a.status === "cancelled").length,
      totalGain,
      avgGain,
      successRate: alertHistory.length > 0 ? (triggered.length / alertHistory.length * 100) : 0
    };
  };

  const stats = getStats();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-enhanced py-8">
      <h1 className="text-3xl font-bold mb-6">Alert History</h1>
      <div className="table-responsive">
        {/* history content */}
      </div>
    </div>
  );
};

export default AlertHistory;