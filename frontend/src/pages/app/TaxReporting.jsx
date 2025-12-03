import React, { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import {
  Download,
  FileText,
  Calculator,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  AlertCircle,
  Info,
  BarChart3,
  PieChart,
  Filter,
  Loader2,
  FileSpreadsheet,
} from "lucide-react";
import { toast } from "sonner";
import { format, startOfYear, endOfYear, isWithinInterval, parseISO } from "date-fns";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import SEO from "../../components/SEO";

const COLORS = ["#10B981", "#EF4444", "#F59E0B", "#3B82F6", "#8B5CF6", "#EC4899"];

// Tax Reporting - Phase 9 Retention Feature
export default function TaxReporting() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());
  const [activeTab, setActiveTab] = useState("summary");
  const [isLoading, setIsLoading] = useState(false);

  // Demo data - In production, this would come from the backend
  const tradeData = useMemo(() => {
    const trades = JSON.parse(localStorage.getItem("trading_journal") || "[]");
    return trades.filter((trade) => {
      try {
        const tradeDate = parseISO(trade.date);
        const yearStart = startOfYear(new Date(parseInt(selectedYear), 0, 1));
        const yearEnd = endOfYear(new Date(parseInt(selectedYear), 0, 1));
        return trade.status !== "open" && isWithinInterval(tradeDate, { start: yearStart, end: yearEnd });
      } catch {
        return false;
      }
    });
  }, [selectedYear]);

  // Calculate tax metrics
  const taxMetrics = useMemo(() => {
    let shortTermGains = 0;
    let shortTermLosses = 0;
    let longTermGains = 0;
    let longTermLosses = 0;

    tradeData.forEach((trade) => {
      const pnl = trade.pnl || 0;
      // For simplicity, assume all trades are short-term (held < 1 year)
      // In production, you'd track holding period
      if (pnl >= 0) {
        shortTermGains += pnl;
      } else {
        shortTermLosses += Math.abs(pnl);
      }
    });

    const netShortTerm = shortTermGains - shortTermLosses;
    const netLongTerm = longTermGains - longTermLosses;
    const totalGains = shortTermGains + longTermGains;
    const totalLosses = shortTermLosses + longTermLosses;
    const netGainLoss = netShortTerm + netLongTerm;

    // Wash sale would require more complex tracking
    const washSaleAdjustment = 0;

    // Capital loss carryover limit
    const capitalLossLimit = 3000;
    const deductibleLoss = Math.min(totalLosses, totalGains + capitalLossLimit);
    const carryoverLoss = Math.max(0, totalLosses - deductibleLoss);

    return {
      shortTermGains,
      shortTermLosses,
      netShortTerm,
      longTermGains,
      longTermLosses,
      netLongTerm,
      totalGains,
      totalLosses,
      netGainLoss,
      washSaleAdjustment,
      deductibleLoss,
      carryoverLoss,
      totalTrades: tradeData.length,
    };
  }, [tradeData]);

  // Monthly breakdown for chart
  const monthlyData = useMemo(() => {
    const months = Array.from({ length: 12 }, (_, i) => ({
      month: format(new Date(2024, i, 1), "MMM"),
      gains: 0,
      losses: 0,
    }));

    tradeData.forEach((trade) => {
      try {
        const month = new Date(trade.date).getMonth();
        if (trade.pnl >= 0) {
          months[month].gains += trade.pnl;
        } else {
          months[month].losses += Math.abs(trade.pnl);
        }
      } catch {}
    });

    return months;
  }, [tradeData]);

  // Category breakdown for pie chart
  const categoryData = useMemo(() => {
    const categories = {};
    tradeData.forEach((trade) => {
      const cat = trade.strategy || "Other";
      if (!categories[cat]) categories[cat] = 0;
      categories[cat] += Math.abs(trade.pnl || 0);
    });
    return Object.entries(categories).map(([name, value]) => ({ name, value }));
  }, [tradeData]);

  const handleExportCSV = () => {
    if (tradeData.length === 0) {
      toast.error("No trade data to export");
      return;
    }

    const headers = [
      "Date",
      "Symbol",
      "Type",
      "Entry Price",
      "Exit Price",
      "Shares",
      "Gross P&L",
      "Status",
      "Strategy",
    ];

    const rows = tradeData.map((trade) => [
      format(new Date(trade.date), "yyyy-MM-dd"),
      trade.symbol,
      trade.type,
      trade.entry_price,
      trade.exit_price || "",
      trade.shares,
      trade.pnl?.toFixed(2) || "0.00",
      trade.status,
      trade.strategy || "",
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `tax_report_${selectedYear}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success("Report exported!");
  };

  const handleExport8949 = () => {
    toast.info("Form 8949 export coming soon! Please use CSV export for now.");
  };

  const years = ["2025", "2024", "2023", "2022"];

  return (
    <div className="container mx-auto px-4 py-6 max-w-6xl" data-testid="tax-reporting-page">
      <SEO
        title="Tax Reporting | Trade Scan Pro"
        description="Generate tax reports for your trading activity"
      />

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg">
              <Calculator className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Tax Reporting</h1>
              <p className="text-gray-500">Capital gains and losses summary for tax filing</p>
            </div>
          </div>
          <Select value={selectedYear} onValueChange={setSelectedYear}>
            <SelectTrigger className="w-32">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {years.map((year) => (
                <SelectItem key={year} value={year}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Disclaimer */}
      <Alert className="mb-6 bg-yellow-50 border-yellow-200">
        <AlertCircle className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-700">
          <strong>Disclaimer:</strong> This is for informational purposes only. Please consult a qualified tax
          professional for advice. Tax calculations may not account for all scenarios.
        </AlertDescription>
      </Alert>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Gains</p>
                <p className="text-2xl font-bold text-green-600">
                  ${taxMetrics.totalGains.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-200" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Losses</p>
                <p className="text-2xl font-bold text-red-600">
                  ${taxMetrics.totalLosses.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-200" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Net Gain/Loss</p>
                <p className={`text-2xl font-bold ${taxMetrics.netGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
                  ${Math.abs(taxMetrics.netGainLoss).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-gray-200" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Trades</p>
                <p className="text-2xl font-bold">{taxMetrics.totalTrades}</p>
              </div>
              <FileText className="h-8 w-8 text-gray-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="summary" className="gap-2">
            <FileText className="h-4 w-4" />
            Summary
          </TabsTrigger>
          <TabsTrigger value="breakdown" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Breakdown
          </TabsTrigger>
          <TabsTrigger value="transactions" className="gap-2">
            <Filter className="h-4 w-4" />
            Transactions
          </TabsTrigger>
        </TabsList>

        {/* Summary Tab */}
        <TabsContent value="summary" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Short-Term */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Badge variant="outline">Short-Term</Badge>
                  Held 1 Year or Less
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Gains</span>
                  <span className="font-semibold text-green-600">
                    ${taxMetrics.shortTermGains.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Losses</span>
                  <span className="font-semibold text-red-600">
                    (${taxMetrics.shortTermLosses.toFixed(2)})
                  </span>
                </div>
                <hr />
                <div className="flex justify-between">
                  <span className="font-medium">Net Short-Term</span>
                  <span className={`font-bold ${taxMetrics.netShortTerm >= 0 ? "text-green-600" : "text-red-600"}`}>
                    ${taxMetrics.netShortTerm.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 flex items-start gap-1">
                  <Info className="h-3 w-3 mt-0.5 shrink-0" />
                  Taxed as ordinary income (10-37% depending on bracket)
                </p>
              </CardContent>
            </Card>

            {/* Long-Term */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Badge variant="outline" className="bg-blue-50">
                    Long-Term
                  </Badge>
                  Held More Than 1 Year
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Gains</span>
                  <span className="font-semibold text-green-600">
                    ${taxMetrics.longTermGains.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Losses</span>
                  <span className="font-semibold text-red-600">
                    (${taxMetrics.longTermLosses.toFixed(2)})
                  </span>
                </div>
                <hr />
                <div className="flex justify-between">
                  <span className="font-medium">Net Long-Term</span>
                  <span className={`font-bold ${taxMetrics.netLongTerm >= 0 ? "text-green-600" : "text-red-600"}`}>
                    ${taxMetrics.netLongTerm.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 flex items-start gap-1">
                  <Info className="h-3 w-3 mt-0.5 shrink-0" />
                  Preferential rates (0%, 15%, or 20%)
                </p>
              </CardContent>
            </Card>

            {/* Additional Info */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Tax Considerations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-sm text-gray-500">Wash Sale Adjustment</p>
                    <p className="text-xl font-semibold">${taxMetrics.washSaleAdjustment.toFixed(2)}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Losses from selling and rebuying within 30 days
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Deductible Loss (max $3,000)</p>
                    <p className="text-xl font-semibold">${taxMetrics.deductibleLoss.toFixed(2)}</p>
                    <p className="text-xs text-gray-400 mt-1">Maximum loss deduction against ordinary income</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Loss Carryover</p>
                    <p className="text-xl font-semibold">${taxMetrics.carryoverLoss.toFixed(2)}</p>
                    <p className="text-xs text-gray-400 mt-1">Excess losses carried to future years</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Export Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export Reports</CardTitle>
              <CardDescription>Download tax documents for your records</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-4">
              <Button onClick={handleExportCSV} variant="outline" className="gap-2">
                <FileSpreadsheet className="h-4 w-4" />
                Export CSV
              </Button>
              <Button onClick={handleExport8949} variant="outline" className="gap-2">
                <FileText className="h-4 w-4" />
                Form 8949
              </Button>
              <Button variant="outline" className="gap-2" disabled>
                <Download className="h-4 w-4" />
                Schedule D
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Breakdown Tab */}
        <TabsContent value="breakdown" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Monthly Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Monthly Gains & Losses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={monthlyData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                      <Bar dataKey="gains" fill="#10B981" name="Gains" />
                      <Bar dataKey="losses" fill="#EF4444" name="Losses" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Category Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>By Strategy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {categoryData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={categoryData}
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {categoryData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                        <Legend />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">
                      No strategy data available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Transactions Tab */}
        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle>Transaction History</CardTitle>
              <CardDescription>{tradeData.length} closed trades in {selectedYear}</CardDescription>
            </CardHeader>
            <CardContent>
              {tradeData.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead className="text-right">Entry</TableHead>
                        <TableHead className="text-right">Exit</TableHead>
                        <TableHead className="text-right">Shares</TableHead>
                        <TableHead className="text-right">P&L</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {tradeData.map((trade, index) => (
                        <TableRow key={index}>
                          <TableCell>{format(new Date(trade.date), "MMM d, yyyy")}</TableCell>
                          <TableCell className="font-medium">{trade.symbol}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{trade.type}</Badge>
                          </TableCell>
                          <TableCell className="text-right">${trade.entry_price}</TableCell>
                          <TableCell className="text-right">${trade.exit_price || "-"}</TableCell>
                          <TableCell className="text-right">{trade.shares}</TableCell>
                          <TableCell className={`text-right font-semibold ${trade.pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {trade.pnl >= 0 ? "+" : ""}${trade.pnl?.toFixed(2) || "0.00"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="font-medium text-gray-900">No Transactions</h3>
                  <p className="text-gray-500">No closed trades found for {selectedYear}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
