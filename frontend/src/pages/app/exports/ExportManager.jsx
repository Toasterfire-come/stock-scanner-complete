import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Progress } from '../../../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { 
  Download, 
  FileText, 
  Calendar, 
  History, 
  Plus,
  Database,
  BarChart,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/SecureAuthContext';
import { 
  exportStocksCSV, 
  exportPortfolioCSV, 
  exportWatchlistCSV,
  downloadReport,
  listExportHistory,
  getCurrentApiUsage,
  getPlanLimits
} from '../../../api/client';
import { downloadBlob } from '../../../lib/downloads';
import { toast } from 'sonner';
import logger from '../../../lib/logger';

const ExportManager = () => {
  const { user } = useAuth();
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [usage, setUsage] = useState({ current: 0, limit: 0 });

  useEffect(() => {
    loadExportHistory();
    loadUsageInfo();
  }, []);

  const loadExportHistory = async () => {
    try {
      const res = await listExportHistory();
      if (res?.success) {
        const items = (res.data || []).map((j) => ({
          id: j.id,
          type: j.type,
          name: j.name,
          format: String(j.format || 'csv').toUpperCase(),
          size: j.size || null,
          records: j.records || null,
          status: j.status,
          created: j.created_at || j.created,
          downloadUrl: j.status === 'completed' ? `/api/reports/${j.id}/download` : null
        }));
        setExports(items);
        return;
      }
    } catch (error) {
      logger.error('Failed to load export history:', error);
    }
    setExports([]);
  };

  const loadUsageInfo = async () => {
    try {
      const currentUsage = getCurrentApiUsage();
      const limits = getPlanLimits();
      setUsage({
        current: currentUsage,
        limit: limits.monthlyApi === Infinity ? 0 : limits.monthlyApi
      });
    } catch (error) {
      logger.error('Failed to load usage info:', error);
    }
  };

  const handleQuickExport = async (type) => {
    setLoading(true);
    try {
      let blob;
      let filename;
      
      switch (type) {
        case 'stocks':
          blob = await exportStocksCSV({ limit: 1000 });
          filename = `stocks-${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'portfolio':
          blob = await exportPortfolioCSV();
          filename = `portfolio-${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'watchlist':
          blob = await exportWatchlistCSV();
          filename = `watchlist-${new Date().toISOString().split('T')[0]}.csv`;
          break;
        default:
          throw new Error('Unknown export type');
      }

      downloadBlob(blob, filename);

      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} data exported successfully`);
      
      // Refresh export history
      await loadExportHistory();
    } catch (error) {
      logger.error(`Failed to export ${type}:`, error);
      toast.error(`Failed to export ${type} data`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (exportItem) => {
    if (exportItem.status !== 'completed') return;
    
    try {
      // If it's a backend-generated report job, download via report endpoint.
      if (exportItem.type === 'custom_report') {
        const blob = await downloadReport(exportItem.id);
        downloadBlob(blob, `${exportItem.name}.${exportItem.format.toLowerCase()}`);
      } else {
        // Quick exports are generated on-demand
        await handleQuickExport(exportItem.type);
      }
      toast.success('Download started');
    } catch (error) {
      logger.error('Download failed:', error);
      toast.error('Download failed');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const quickExportOptions = [
    {
      type: 'stocks',
      title: 'Stocks Data',
      description: 'Export complete stock database with current prices',
      icon: Database,
      format: 'CSV',
      estimatedSize: '~2.5 MB'
    },
    {
      type: 'portfolio',
      title: 'Portfolio Holdings',
      description: 'Export your current portfolio positions and performance',
      icon: TrendingUp,
      format: 'CSV',
      estimatedSize: '~100 KB'
    },
    {
      type: 'watchlist',
      title: 'Watchlists',
      description: 'Export all your watchlists and tracked stocks',
      icon: Users,
      format: 'CSV',
      estimatedSize: '~50 KB'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Export Manager</h1>
              <p className="text-gray-600">Export your data, create custom reports, and manage scheduled exports</p>
            </div>
            <div className="flex items-center gap-3">
              {usage.limit > 0 && (
                <div className="text-right">
                  <div className="text-sm text-gray-600">API Usage This Month</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {usage.current.toLocaleString()} / {usage.limit.toLocaleString()}
                  </div>
                  <Progress 
                    value={(usage.current / usage.limit) * 100} 
                    className="w-32 mt-1"
                  />
                </div>
              )}
              <Button asChild className="bg-blue-600 hover:bg-blue-700">
                <Link to="/app/exports/custom-report">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Report
                </Link>
              </Button>
            </div>
          </div>
        </div>

        <Tabs defaultValue="quick-export" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="quick-export">Quick Export</TabsTrigger>
            <TabsTrigger value="history">Export History</TabsTrigger>
            <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
            <TabsTrigger value="reports">Custom Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="quick-export" className="space-y-6">
            <div className="grid md:grid-cols-3 gap-6">
              {quickExportOptions.map((option) => (
                <Card key={option.type} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4 mb-4">
                      <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <option.icon className="h-6 w-6 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{option.title}</h3>
                        <p className="text-sm text-gray-600 mb-2">{option.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Format: {option.format}</span>
                          <span>Size: {option.estimatedSize}</span>
                        </div>
                      </div>
                    </div>
                    <Button 
                      onClick={() => handleQuickExport(option.type)}
                      disabled={loading}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export Now
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Alert className="border-blue-200 bg-blue-50">
              <Download className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Quick Export Tips:</strong> Exports are generated in real-time and include the most current data. 
                Large exports may take a few seconds to prepare. All exports are automatically tracked in your history.
              </AlertDescription>
            </Alert>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Recent Exports</h2>
              <Button 
                variant="outline" 
                onClick={loadExportHistory}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>

            <div className="space-y-4">
              {exports.map((exportItem) => (
                <Card key={exportItem.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-start gap-4">
                        <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                          <FileText className="h-6 w-6 text-gray-600" />
                        </div>
                        <div>
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="font-semibold text-gray-900">{exportItem.name}</h3>
                            <Badge className={`text-xs ${getStatusColor(exportItem.status)}`}>
                              <div className="flex items-center gap-1">
                                {getStatusIcon(exportItem.status)}
                                {exportItem.status}
                              </div>
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>Format: {exportItem.format} • Size: {exportItem.size}</div>
                            {exportItem.records && (
                              <div>Records: {exportItem.records.toLocaleString()}</div>
                            )}
                            <div>Created: {formatDate(exportItem.created)}</div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {exportItem.status === 'completed' && (
                          <Button 
                            size="sm"
                            onClick={() => handleDownload(exportItem)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </Button>
                        )}
                        {exportItem.status === 'processing' && (
                          <div className="text-sm text-blue-600 flex items-center gap-2">
                            <RefreshCw className="h-4 w-4 animate-spin" />
                            Processing...
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {exports.length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Exports Yet</h3>
                    <p className="text-gray-600 mb-4">Create your first export using the Quick Export options above.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="scheduled" className="space-y-6">
            <div className="text-center">
              <Card>
                <CardContent className="py-12">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Scheduled Exports</h3>
                  <p className="text-gray-600 mb-4">
                    Set up automated exports to run on a schedule. Perfect for regular reporting and data backups.
                  </p>
                  <Button asChild className="bg-blue-600 hover:bg-blue-700">
                    <Link to="/app/exports/scheduled">
                      Set Up Scheduled Export
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <div className="text-center">
              <Card>
                <CardContent className="py-12">
                  <BarChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Custom Reports</h3>
                  <p className="text-gray-600 mb-4">
                    Create detailed custom reports with advanced filtering, calculations, and professional formatting.
                  </p>
                  <Button asChild className="bg-blue-600 hover:bg-blue-700">
                    <Link to="/app/exports/custom-report">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Custom Report
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Export Guidelines */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Export Guidelines</CardTitle>
            <CardDescription>Important information about data exports and limitations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Data Freshness</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Stock data: Real-time (Gold) or 15-min delayed</li>
                  <li>• Portfolio data: Real-time</li>
                  <li>• Market data: Updated every minute</li>
                  <li>• Reports: Generated with current data</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Export Limits</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Free plan: 5 exports per month</li>
                  <li>• Paid plans: Unlimited exports</li>
                  <li>• File retention: 30 days</li>
                  <li>• Max file size: 100MB</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExportManager;