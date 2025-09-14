import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Search, Download, Filter, TrendingUp, TrendingDown, Calendar, Clock } from "lucide-react";
import { toast } from "sonner";

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
      // Simulate fetching alert history
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockHistory = [
        {
          id: 1,
          ticker: "AAPL",
          targetPrice: 200.00,
          triggerPrice: 202.15,
          condition: "above",
          status: "triggered",
          createdAt: "2024-01-10T09:30:00Z",
          triggeredAt: "2024-01-12T14:25:00Z",
          email: "user@example.com",
          gain: 2.15
        },
        {
          id: 2,
          ticker: "MSFT",
          targetPrice: 450.00,
          triggerPrice: 445.80,
          condition: "below",
          status: "triggered",
          createdAt: "2024-01-08T11:15:00Z",
          triggeredAt: "2024-01-11T10:30:00Z",
          email: "user@example.com",
          gain: -4.20
        },
        {
          id: 3,
          ticker: "GOOGL",
          targetPrice: 140.00,
          triggerPrice: null,
          condition: "above",
          status: "expired",
          createdAt: "2024-01-05T16:20:00Z",
          expiredAt: "2024-01-15T16:20:00Z",
          email: "user@example.com",
          gain: null
        },
        {
          id: 4,
          ticker: "TSLA",
          targetPrice: 280.00,
          triggerPrice: null,
          condition: "above",
          status: "cancelled",
          createdAt: "2024-01-07T13:45:00Z",
          cancelledAt: "2024-01-09T09:15:00Z",
          email: "user@example.com",
          gain: null
        },
        {
          id: 5,
          ticker: "NVDA",
          targetPrice: 120.00,
          triggerPrice: 125.30,
          condition: "above",
          status: "triggered",
          createdAt: "2024-01-06T08:00:00Z",
          triggeredAt: "2024-01-08T11:45:00Z",
          email: "user@example.com",
          gain: 5.30
        }
      ];

      setAlertHistory(mockHistory);
    } catch (error) {
      toast.error("Failed to fetch alert history");
    } finally {
      setIsLoading(false);
    }
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
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alert History</h1>
          <p className="text-gray-600 mt-2">Track your past price alerts and their outcomes</p>
        </div>
        <Button onClick={exportHistory}>
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      <div className="grid gap-6">
        <div className="grid md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
              <div className="text-sm text-gray-600">Total Alerts</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-green-600">{stats.triggered}</div>
              <div className="text-sm text-gray-600">Triggered</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.successRate.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className={`text-2xl font-bold ${stats.totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatGain(stats.totalGain)}
              </div>
              <div className="text-sm text-gray-600">Total Gain/Loss</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Filter & Search</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by ticker..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full lg:w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={dateFilter} onValueChange={setDateFilter}>
                <SelectTrigger className="w-full lg:w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {dateOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alert History ({filteredHistory.length} results)</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredHistory.length > 0 ? (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Ticker</TableHead>
                      <TableHead>Target Price</TableHead>
                      <TableHead>Trigger Price</TableHead>
                      <TableHead>Condition</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Completed</TableHead>
                      <TableHead>Gain/Loss</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredHistory.map((alert) => (
                      <TableRow key={alert.id}>
                        <TableCell className="font-semibold">{alert.ticker}</TableCell>
                        <TableCell>{formatPrice(alert.targetPrice)}</TableCell>
                        <TableCell>{formatPrice(alert.triggerPrice)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {getConditionIcon(alert.condition)}
                            {alert.condition}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(alert.status)}>
                            {alert.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-gray-400" />
                            {new Date(alert.createdAt).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {alert.triggeredAt ? (
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3 text-gray-400" />
                              {new Date(alert.triggeredAt).toLocaleDateString()}
                            </div>
                          ) : alert.expiredAt ? (
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3 text-gray-400" />
                              {new Date(alert.expiredAt).toLocaleDateString()}
                            </div>
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell>
                          <span className={`font-medium ${alert.gain !== null ? (alert.gain >= 0 ? 'text-green-600' : 'text-red-600') : 'text-gray-500'}`}>
                            {formatGain(alert.gain)}
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">No alert history found</div>
                <Button onClick={() => {
                  setSearchTerm("");
                  setStatusFilter("all");
                  setDateFilter("all");
                }}>
                  Clear Filters
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AlertHistory;