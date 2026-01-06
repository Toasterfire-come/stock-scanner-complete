import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Textarea } from '../../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Checkbox } from '../../../components/ui/checkbox';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Separator } from '../../../components/ui/separator';
import { 
  FileText, 
  Plus, 
  Trash2, 
  Play, 
  Download,
  Filter,
  BarChart3,
  Calendar,
  Settings,
  Eye,
  Save,
  Copy
} from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { generateCustomReport, downloadReport } from '../../../api/client';
import { toast } from 'sonner';
import logger from '../../../lib/logger';

const CustomReportBuilder = () => {
  const { user } = useAuth();
  const [reportConfig, setReportConfig] = useState({
    name: '',
    description: '',
    type: 'portfolio_summary',
    format: 'csv',
    data_sources: [],
    filters: [],
    columns: [],
    date_range: 'last_30_days',
    custom_date_start: '',
    custom_date_end: '',
    include_charts: true,
    include_summary: true,
    schedule_enabled: false,
    schedule_frequency: 'weekly'
  });
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  const reportTypes = [
    {
      value: 'portfolio_summary',
      label: 'Portfolio Summary',
      description: 'Comprehensive portfolio performance and holdings analysis'
    },
    {
      value: 'performance_analysis',
      label: 'Performance Analysis',
      description: 'Detailed performance metrics and comparisons'
    },
    {
      value: 'risk_assessment',
      label: 'Risk Assessment',
      description: 'Risk metrics, diversification analysis, and recommendations'
    },
    {
      value: 'dividend_report',
      label: 'Dividend Report',
      description: 'Dividend income tracking and projections'
    },
    {
      value: 'sector_analysis',
      label: 'Sector Analysis',
      description: 'Sector allocation and performance breakdown'
    },
    {
      value: 'watchlist_report',
      label: 'Watchlist Report',
      description: 'Analysis of stocks in your watchlists'
    },
    {
      value: 'custom',
      label: 'Custom Report',
      description: 'Build a completely custom report from scratch'
    }
  ];

  const dataSourceOptions = [
    { value: 'portfolio', label: 'Portfolio Holdings', description: 'Your current portfolio positions' },
    { value: 'transactions', label: 'Transaction History', description: 'Buy/sell transaction records' },
    { value: 'watchlists', label: 'Watchlists', description: 'Stocks in your watchlists' },
    { value: 'alerts', label: 'Alerts', description: 'Price alert history and status' },
    { value: 'market_data', label: 'Market Data', description: 'Current market prices and statistics' },
    { value: 'news', label: 'News & Events', description: 'Relevant news and market events' }
  ];

  const columnOptions = {
    portfolio: [
      { value: 'symbol', label: 'Symbol' },
      { value: 'company_name', label: 'Company Name' },
      { value: 'shares', label: 'Shares' },
      { value: 'avg_cost', label: 'Average Cost' },
      { value: 'current_price', label: 'Current Price' },
      { value: 'total_value', label: 'Total Value' },
      { value: 'gain_loss', label: 'Gain/Loss ($)' },
      { value: 'gain_loss_percent', label: 'Gain/Loss (%)' },
      { value: 'sector', label: 'Sector' },
      { value: 'market_cap', label: 'Market Cap' }
    ],
    market_data: [
      { value: 'symbol', label: 'Symbol' },
      { value: 'company_name', label: 'Company Name' },
      { value: 'current_price', label: 'Current Price' },
      { value: 'change_percent', label: 'Change %' },
      { value: 'volume', label: 'Volume' },
      { value: 'market_cap', label: 'Market Cap' },
      { value: 'pe_ratio', label: 'P/E Ratio' },
      { value: 'dividend_yield', label: 'Dividend Yield' }
    ]
  };

  const handleInputChange = (field, value) => {
    setReportConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleDataSourceToggle = (source) => {
    setReportConfig(prev => ({
      ...prev,
      data_sources: prev.data_sources.includes(source)
        ? prev.data_sources.filter(s => s !== source)
        : [...prev.data_sources, source]
    }));
  };

  const handleColumnToggle = (column) => {
    setReportConfig(prev => ({
      ...prev,
      columns: prev.columns.includes(column)
        ? prev.columns.filter(c => c !== column)
        : [...prev.columns, column]
    }));
  };

  const addFilter = () => {
    setReportConfig(prev => ({
      ...prev,
      filters: [...prev.filters, { field: '', operator: 'equals', value: '' }]
    }));
  };

  const removeFilter = (index) => {
    setReportConfig(prev => ({
      ...prev,
      filters: prev.filters.filter((_, i) => i !== index)
    }));
  };

  const updateFilter = (index, field, value) => {
    setReportConfig(prev => ({
      ...prev,
      filters: prev.filters.map((filter, i) => 
        i === index ? { ...filter, [field]: value } : filter
      )
    }));
  };

  const handlePreview = async () => {
    if (!reportConfig.name.trim()) {
      toast.error('Please enter a report name');
      return;
    }

    if (reportConfig.data_sources.length === 0) {
      toast.error('Please select at least one data source');
      return;
    }

    setLoading(true);
    try {
      // Generate preview data (mock for now)
      const mockPreviewData = {
        summary: {
          total_records: 145,
          date_range: reportConfig.date_range,
          generated_at: new Date().toISOString()
        },
        sample_data: [
          { symbol: 'AAPL', company_name: 'Apple Inc.', current_price: 150.25, change_percent: 2.3 },
          { symbol: 'GOOGL', company_name: 'Alphabet Inc.', current_price: 2750.80, change_percent: -1.2 },
          { symbol: 'MSFT', company_name: 'Microsoft Corp.', current_price: 380.45, change_percent: 0.8 }
        ]
      };
      
      setPreviewData(mockPreviewData);
      setShowPreview(true);
      toast.success('Preview generated successfully');
    } catch (error) {
      logger.error('Failed to generate preview:', error);
      toast.error('Failed to generate preview');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!reportConfig.name.trim()) {
      toast.error('Please enter a report name');
      return;
    }

    if (reportConfig.data_sources.length === 0) {
      toast.error('Please select at least one data source');
      return;
    }

    setLoading(true);
    try {
      if (String(reportConfig.format).toLowerCase() !== 'csv') {
        toast.error('Only CSV reports are supported right now.');
        setLoading(false);
        return;
      }
      const response = await generateCustomReport(reportConfig);
      if (response.success) {
        try {
          const reportId = response.report_id || response.reportId || response.id;
          if (reportId) {
            const blob = await downloadReport(reportId);
            const filename = `${reportConfig.name || 'report'}.csv`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
          }
        } catch {}
        toast.success('Report generated. Download started.');
      } else {
        toast.error(response.error || 'Failed to generate report');
      }
    } catch (error) {
      logger.error('Failed to generate report:', error);
      toast.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const availableColumns = reportConfig.data_sources.length > 0 
    ? reportConfig.data_sources.flatMap(source => columnOptions[source] || [])
    : [];

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Custom Report Builder</h1>
              <p className="text-gray-600">Create detailed custom reports with advanced filtering and formatting</p>
            </div>
            <div className="flex items-center gap-3">
              <Button 
                variant="outline"
                onClick={handlePreview}
                disabled={loading}
              >
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button 
                onClick={handleGenerate}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Generate Report
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="basic" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="basic">Basic Info</TabsTrigger>
                <TabsTrigger value="data">Data Sources</TabsTrigger>
                <TabsTrigger value="columns">Columns</TabsTrigger>
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Report Configuration</CardTitle>
                    <CardDescription>Basic report settings and type selection</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="name">Report Name *</Label>
                      <Input
                        id="name"
                        value={reportConfig.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="Q1 Portfolio Performance Report"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        value={reportConfig.description}
                        onChange={(e) => handleInputChange('description', e.target.value)}
                        placeholder="Detailed analysis of portfolio performance for Q1 2024..."
                        rows={3}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="type">Report Type</Label>
                      <Select 
                        value={reportConfig.type} 
                        onValueChange={(value) => handleInputChange('type', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {reportTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              <div>
                                <div className="font-medium">{type.label}</div>
                                <div className="text-sm text-gray-600">{type.description}</div>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="format">Output Format</Label>
                        <Select 
                          value={reportConfig.format} 
                          onValueChange={(value) => handleInputChange('format', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="csv">CSV</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="date_range">Date Range</Label>
                        <Select 
                          value={reportConfig.date_range} 
                          onValueChange={(value) => handleInputChange('date_range', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="last_7_days">Last 7 Days</SelectItem>
                            <SelectItem value="last_30_days">Last 30 Days</SelectItem>
                            <SelectItem value="last_3_months">Last 3 Months</SelectItem>
                            <SelectItem value="last_6_months">Last 6 Months</SelectItem>
                            <SelectItem value="last_year">Last Year</SelectItem>
                            <SelectItem value="ytd">Year to Date</SelectItem>
                            <SelectItem value="custom">Custom Range</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {reportConfig.date_range === 'custom' && (
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="custom_date_start">Start Date</Label>
                          <Input
                            id="custom_date_start"
                            type="date"
                            value={reportConfig.custom_date_start}
                            onChange={(e) => handleInputChange('custom_date_start', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="custom_date_end">End Date</Label>
                          <Input
                            id="custom_date_end"
                            type="date"
                            value={reportConfig.custom_date_end}
                            onChange={(e) => handleInputChange('custom_date_end', e.target.value)}
                          />
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="data" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Data Sources</CardTitle>
                    <CardDescription>Select the data sources to include in your report</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {dataSourceOptions.map((source) => (
                        <div key={source.value} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                          <Checkbox
                            id={source.value}
                            checked={reportConfig.data_sources.includes(source.value)}
                            onCheckedChange={() => handleDataSourceToggle(source.value)}
                          />
                          <div className="flex-1">
                            <label
                              htmlFor={source.value}
                              className="text-sm font-medium text-gray-900 cursor-pointer"
                            >
                              {source.label}
                            </label>
                            <p className="text-xs text-gray-600">{source.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Filters */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Filter className="h-5 w-5" />
                      Data Filters
                    </CardTitle>
                    <CardDescription>Add filters to customize your data selection</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {reportConfig.filters.map((filter, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                        <Select 
                          value={filter.field} 
                          onValueChange={(value) => updateFilter(index, 'field', value)}
                        >
                          <SelectTrigger className="w-40">
                            <SelectValue placeholder="Field" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="symbol">Symbol</SelectItem>
                            <SelectItem value="sector">Sector</SelectItem>
                            <SelectItem value="market_cap">Market Cap</SelectItem>
                            <SelectItem value="price">Price</SelectItem>
                            <SelectItem value="change_percent">Change %</SelectItem>
                          </SelectContent>
                        </Select>

                        <Select 
                          value={filter.operator} 
                          onValueChange={(value) => updateFilter(index, 'operator', value)}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="equals">Equals</SelectItem>
                            <SelectItem value="not_equals">Not Equals</SelectItem>
                            <SelectItem value="greater_than">Greater Than</SelectItem>
                            <SelectItem value="less_than">Less Than</SelectItem>
                            <SelectItem value="contains">Contains</SelectItem>
                          </SelectContent>
                        </Select>

                        <Input
                          value={filter.value}
                          onChange={(e) => updateFilter(index, 'value', e.target.value)}
                          placeholder="Value"
                          className="flex-1"
                        />

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => removeFilter(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}

                    <Button
                      variant="outline"
                      onClick={addFilter}
                      className="w-full"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Filter
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="columns" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Column Selection</CardTitle>
                    <CardDescription>Choose which columns to include in your report</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {availableColumns.length > 0 ? (
                      <div className="grid md:grid-cols-2 gap-3">
                        {availableColumns.map((column) => (
                          <div key={column.value} className="flex items-center space-x-2">
                            <Checkbox
                              id={column.value}
                              checked={reportConfig.columns.includes(column.value)}
                              onCheckedChange={() => handleColumnToggle(column.value)}
                            />
                            <label
                              htmlFor={column.value}
                              className="text-sm font-medium text-gray-900 cursor-pointer"
                            >
                              {column.label}
                            </label>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <Alert>
                        <AlertDescription>
                          Please select data sources first to see available columns.
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="advanced" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Advanced Options</CardTitle>
                    <CardDescription>Additional formatting and presentation options</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-base font-medium">Include Charts</Label>
                          <p className="text-sm text-gray-600">Add visual charts and graphs to the report</p>
                        </div>
                        <Checkbox
                          checked={reportConfig.include_charts}
                          onCheckedChange={(checked) => handleInputChange('include_charts', checked)}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-base font-medium">Include Summary</Label>
                          <p className="text-sm text-gray-600">Add executive summary and key metrics</p>
                        </div>
                        <Checkbox
                          checked={reportConfig.include_summary}
                          onCheckedChange={(checked) => handleInputChange('include_summary', checked)}
                        />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-base font-medium">Enable Scheduling</Label>
                          <p className="text-sm text-gray-600">Automatically generate this report on a schedule</p>
                        </div>
                        <Checkbox
                          checked={reportConfig.schedule_enabled}
                          onCheckedChange={(checked) => handleInputChange('schedule_enabled', checked)}
                        />
                      </div>

                      {reportConfig.schedule_enabled && (
                        <div className="space-y-2 ml-6">
                          <Label htmlFor="schedule_frequency">Frequency</Label>
                          <Select 
                            value={reportConfig.schedule_frequency} 
                            onValueChange={(value) => handleInputChange('schedule_frequency', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="daily">Daily</SelectItem>
                              <SelectItem value="weekly">Weekly</SelectItem>
                              <SelectItem value="monthly">Monthly</SelectItem>
                              <SelectItem value="quarterly">Quarterly</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Preview Panel */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Report Preview
                </CardTitle>
              </CardHeader>
              <CardContent>
                {showPreview && previewData ? (
                  <div className="space-y-4">
                    <div className="border rounded-lg p-4 bg-gray-50">
                      <h3 className="font-semibold text-gray-900 mb-2">{reportConfig.name}</h3>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>Format: {reportConfig.format.toUpperCase()}</div>
                        <div>Records: {previewData.summary.total_records}</div>
                        <div>Date Range: {reportConfig.date_range.replace(/_/g, ' ')}</div>
                        <div>Sources: {reportConfig.data_sources.length}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Sample Data</h4>
                      <div className="text-xs space-y-1">
                        {previewData.sample_data.map((row, index) => (
                          <div key={index} className="flex justify-between">
                            <span>{row.symbol}</span>
                            <span className={row.change_percent > 0 ? 'text-green-600' : 'text-red-600'}>
                              {row.change_percent}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 text-sm">
                      Configure your report and click Preview to see a sample of the data
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomReportBuilder;