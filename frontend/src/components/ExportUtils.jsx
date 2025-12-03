// Export Utilities - Phase 9 Retention Feature
import React, { useState } from "react";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import { toast } from "sonner";
import { Download, FileSpreadsheet, FileText, Loader2, Calendar } from "lucide-react";
import { format, startOfYear, endOfYear, subYears } from "date-fns";

/**
 * Export Journal Data to CSV
 */
export function exportToCSV(data, filename = "export.csv") {
  if (!data || data.length === 0) {
    toast.error("No data to export");
    return;
  }

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(","),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header];
          // Escape commas and quotes in values
          if (typeof value === "string" && (value.includes(",") || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value ?? "";
        })
        .join(",")
    ),
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
  
  toast.success(`Exported ${data.length} records to ${filename}`);
}

/**
 * Export Journal Data to JSON
 */
export function exportToJSON(data, filename = "export.json") {
  if (!data || data.length === 0) {
    toast.error("No data to export");
    return;
  }

  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
  
  toast.success(`Exported ${data.length} records to ${filename}`);
}

/**
 * Generate Tax Report Data
 */
export function generateTaxReport(entries, year) {
  const yearStart = startOfYear(new Date(year, 0, 1));
  const yearEnd = endOfYear(new Date(year, 0, 1));
  
  const yearEntries = entries.filter((entry) => {
    const entryDate = new Date(entry.date);
    return entryDate >= yearStart && entryDate <= yearEnd && entry.status !== "open";
  });

  // Calculate short-term vs long-term (simplified - assumes all short-term for now)
  const shortTermGains = yearEntries
    .filter((e) => e.pnl > 0)
    .reduce((sum, e) => sum + e.pnl, 0);
  
  const shortTermLosses = yearEntries
    .filter((e) => e.pnl < 0)
    .reduce((sum, e) => sum + Math.abs(e.pnl), 0);
  
  const netShortTerm = shortTermGains - shortTermLosses;
  
  // Format entries for tax reporting
  const taxEntries = yearEntries.map((entry) => ({
    symbol: entry.symbol,
    description: `${entry.side} ${entry.quantity || 0} shares`,
    date_acquired: entry.entry_date || entry.date,
    date_sold: entry.exit_date || entry.date,
    proceeds: entry.exit_price ? (entry.exit_price * (entry.quantity || 1)) : 0,
    cost_basis: entry.entry_price ? (entry.entry_price * (entry.quantity || 1)) : 0,
    gain_loss: entry.pnl || 0,
    holding_period: "Short-term",
    wash_sale: false,
  }));

  return {
    year,
    summary: {
      total_trades: yearEntries.length,
      short_term_gains: shortTermGains,
      short_term_losses: shortTermLosses,
      net_short_term: netShortTerm,
      long_term_gains: 0,
      long_term_losses: 0,
      net_long_term: 0,
      total_net: netShortTerm,
    },
    entries: taxEntries,
  };
}

/**
 * Tax Report Export Dialog Component
 */
export function TaxReportExporter({ entries = [] }) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());
  const [format, setFormat] = useState("csv");
  const [includeDetails, setIncludeDetails] = useState(true);

  const currentYear = new Date().getFullYear();
  const availableYears = Array.from({ length: 5 }, (_, i) => currentYear - i);

  const handleExport = async () => {
    setExporting(true);
    try {
      const report = generateTaxReport(entries, parseInt(selectedYear));
      
      if (report.entries.length === 0) {
        toast.error(`No closed trades found for ${selectedYear}`);
        return;
      }

      const filename = `tax_report_${selectedYear}`;
      
      if (format === "csv") {
        // Export detailed entries
        if (includeDetails) {
          exportToCSV(report.entries, `${filename}_details.csv`);
        }
        
        // Export summary
        const summaryData = [{
          year: report.year,
          total_trades: report.summary.total_trades,
          short_term_gains: report.summary.short_term_gains.toFixed(2),
          short_term_losses: report.summary.short_term_losses.toFixed(2),
          net_short_term: report.summary.net_short_term.toFixed(2),
          total_net_gain_loss: report.summary.total_net.toFixed(2),
        }];
        exportToCSV(summaryData, `${filename}_summary.csv`);
      } else {
        exportToJSON(report, `${filename}.json`);
      }
      
      setOpen(false);
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Failed to generate tax report");
    } finally {
      setExporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2" data-testid="export-tax-report">
          <FileSpreadsheet className="h-4 w-4" />
          Tax Report
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5 text-green-600" />
            Export Tax Report
          </DialogTitle>
          <DialogDescription>
            Generate a tax report of your trading activity for a specific year.
            This report includes all closed positions and can be used for tax preparation.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Tax Year</Label>
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger>
                <Calendar className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availableYears.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label>Export Format</Label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="csv">CSV (Excel compatible)</SelectItem>
                <SelectItem value="json">JSON (Full data)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {format === "csv" && (
            <div className="flex items-center space-x-2">
              <Checkbox
                id="includeDetails"
                checked={includeDetails}
                onCheckedChange={setIncludeDetails}
              />
              <Label htmlFor="includeDetails" className="text-sm">
                Include detailed trade-by-trade breakdown
              </Label>
            </div>
          )}
          
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
            <strong>Disclaimer:</strong> This report is for informational purposes only 
            and should not be considered tax advice. Please consult with a qualified 
            tax professional for your specific situation.
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={exporting} className="gap-2">
            {exporting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export Report
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/**
 * General Data Exporter Component
 */
export function DataExporter({ data, filename = "export", title = "Export Data" }) {
  const [format, setFormat] = useState("csv");

  const handleExport = () => {
    if (format === "csv") {
      exportToCSV(data, `${filename}.csv`);
    } else {
      exportToJSON(data, `${filename}.json`);
    }
  };

  if (!data || data.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={format} onValueChange={setFormat}>
        <SelectTrigger className="w-24">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="csv">CSV</SelectItem>
          <SelectItem value="json">JSON</SelectItem>
        </SelectContent>
      </Select>
      <Button variant="outline" size="sm" onClick={handleExport} className="gap-2">
        <Download className="h-4 w-4" />
        Export
      </Button>
    </div>
  );
}

export default {
  exportToCSV,
  exportToJSON,
  generateTaxReport,
  TaxReportExporter,
  DataExporter,
};
