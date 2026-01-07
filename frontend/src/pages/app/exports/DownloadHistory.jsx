import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Badge } from '../../../components/ui/badge';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { 
  Download, 
  Search, 
  Filter, 
  Calendar, 
  FileText, 
  Trash2,
  RefreshCw,
  CheckCircle,
  Clock,
  AlertTriangle,
  Eye,
  MoreHorizontal,
  Archive
} from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { toast } from 'sonner';
import logger from '../../../lib/logger';
import { listExportHistory, downloadReport } from '../../../api/client';
import { downloadBlob } from '../../../lib/downloads';

const DownloadHistory = () => {
  const { user } = useAuth();
  const [downloads, setDownloads] = useState([]);
  const [filteredDownloads, setFilteredDownloads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [dateRange, setDateRange] = useState('all');

  useEffect(() => {
    loadDownloadHistory();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [downloads, searchTerm, filterType, filterStatus, dateRange]);

  const loadDownloadHistory = async () => {
    setLoading(true);
    try {
      const res = await listExportHistory();
      if (res?.success) {
        const items = (res.data || []).map((j) => ({
          id: j.id,
          name: j.name,
          type: j.type,
          format: String(j.format || 'csv').toUpperCase(),
          size: null,
          status: j.status,
          created_at: j.created_at,
          expires_at: null,
          download_count: Number(j.download_count || 0),
          source: 'backend',
          file_url: j.status === 'completed' ? `/api/reports/${j.id}/download` : null,
          error: j.error || null
        }));
        setDownloads(items);
        return;
      }
      setDownloads([]);
    } catch (error) {
      logger.error('Failed to load download history:', error);
      toast.error('Failed to load download history');
      setDownloads([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = downloads;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(download =>
        download.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        download.type.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(download => download.type === filterType);
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(download => download.status === filterStatus);
    }

    // Date range filter
    if (dateRange !== 'all') {
      const now = new Date();
      const cutoffDate = new Date();
      
      switch (dateRange) {
        case 'today':
          cutoffDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          cutoffDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        default:
          break;
      }
      
      filtered = filtered.filter(download => 
        new Date(download.created_at) >= cutoffDate
      );
    }

    setFilteredDownloads(filtered);
  };

  const handleDownload = async (download) => {
    if (download.status !== 'completed' || !download.file_url) {
      toast.error('File is not available for download');
      return;
    }

    try {
      const blob = await downloadReport(download.id);
      downloadBlob(blob, `${download.name}.${download.format.toLowerCase()}`);
      toast.success(`Downloading ${download.name}...`);
      await loadDownloadHistory();
    } catch (error) {
      logger.error('Download failed:', error);
      toast.error('Download failed');
    }
  };

  const handleDelete = async (id) => {
    try {
      setDownloads(prev => prev.filter(d => d.id !== id));
      toast.success('Download record deleted');
    } catch (error) {
      logger.error('Failed to delete download:', error);
      toast.error('Failed to delete download');
    }
  };

  const handleRetry = async (download) => {
    if (download.status !== 'failed') return;
    
    toast.success(`Retrying export: ${download.name}`);
    setDownloads(prev => prev.map(d => 
      d.id === download.id 
        ? { ...d, status: 'processing' }
        : d
    ));
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

  const getTypeColor = (type) => {
    const colors = {
      portfolio: 'bg-blue-100 text-blue-800',
      stocks: 'bg-green-100 text-green-800',
      watchlist: 'bg-purple-100 text-purple-800',
      custom_report: 'bg-orange-100 text-orange-800',
      alerts: 'bg-red-100 text-red-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const isExpiringSoon = (expiresAt) => {
    if (!expiresAt) return false;
    const expiryDate = new Date(expiresAt);
    const threeDaysFromNow = new Date();
    threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3);
    return expiryDate <= threeDaysFromNow;
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Download History</h1>
              <p className="text-gray-600">View and manage your export and download history</p>
            </div>
            <Button 
              variant="outline"
              onClick={loadDownloadHistory}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="grid md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search downloads..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="portfolio">Portfolio</SelectItem>
                  <SelectItem value="stocks">Stocks</SelectItem>
                  <SelectItem value="watchlist">Watchlist</SelectItem>
                  <SelectItem value="custom_report">Custom Report</SelectItem>
                  <SelectItem value="alerts">Alerts</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>

              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger>
                  <SelectValue placeholder="All Time" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Time</SelectItem>
                  <SelectItem value="today">Today</SelectItem>
                  <SelectItem value="week">Last Week</SelectItem>
                  <SelectItem value="month">Last Month</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Downloads List */}
        <div className="space-y-4">
          {filteredDownloads.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Archive className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {downloads.length === 0 ? 'No Download History' : 'No Results Found'}
                </h3>
                <p className="text-gray-600">
                  {downloads.length === 0 
                    ? 'Your export and download history will appear here.' 
                    : 'Try adjusting your filters to see more results.'
                  }
                </p>
              </CardContent>
            </Card>
          ) : (
            filteredDownloads.map((download) => (
              <Card key={download.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        <FileText className="h-6 w-6 text-gray-600" />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-gray-900">{download.name}</h3>
                          <Badge className={`text-xs ${getStatusColor(download.status)}`}>
                            <div className="flex items-center gap-1">
                              {getStatusIcon(download.status)}
                              {download.status}
                            </div>
                          </Badge>
                          <Badge variant="outline" className={`text-xs ${getTypeColor(download.type)}`}>
                            {download.type.replace('_', ' ')}
                          </Badge>
                          {download.source === 'scheduled' && (
                            <Badge variant="outline" className="text-xs">
                              <Calendar className="h-3 w-3 mr-1" />
                              Scheduled
                            </Badge>
                          )}
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                          <div>
                            <span className="text-gray-500">Format:</span>
                            <span className="ml-1 font-medium">{download.format}</span>
                          </div>
                          
                          {download.size && (
                            <div>
                              <span className="text-gray-500">Size:</span>
                              <span className="ml-1 font-medium">{download.size}</span>
                            </div>
                          )}
                          
                          <div>
                            <span className="text-gray-500">Created:</span>
                            <span className="ml-1 font-medium">{formatDate(download.created_at)}</span>
                          </div>
                          
                          {download.expires_at && (
                            <div>
                              <span className="text-gray-500">Expires:</span>
                              <span className={`ml-1 font-medium ${
                                isExpiringSoon(download.expires_at) ? 'text-amber-600' : ''
                              }`}>
                                {formatDate(download.expires_at)}
                              </span>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>Downloads: {download.download_count}</span>
                        </div>

                        {download.error && (
                          <Alert className="mt-3 border-red-200 bg-red-50">
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                            <AlertDescription className="text-red-800">
                              <strong>Error:</strong> {download.error}
                            </AlertDescription>
                          </Alert>
                        )}

                        {isExpiringSoon(download.expires_at) && download.status === 'completed' && (
                          <Alert className="mt-3 border-amber-200 bg-amber-50">
                            <Clock className="h-4 w-4 text-amber-600" />
                            <AlertDescription className="text-amber-800">
                              This file will expire soon. Download it before {formatDate(download.expires_at)}.
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {download.status === 'completed' && download.file_url && (
                        <Button
                          size="sm"
                          onClick={() => handleDownload(download)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      )}

                      {download.status === 'failed' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRetry(download)}
                        >
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Retry
                        </Button>
                      )}

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(download.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Summary Card */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Download Statistics</CardTitle>
            <CardDescription>Summary of your download activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{downloads.length}</div>
                <div className="text-sm text-gray-600">Total Downloads</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {downloads.filter(d => d.status === 'completed').length}
                </div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {downloads.filter(d => d.status === 'processing').length}
                </div>
                <div className="text-sm text-gray-600">Processing</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {downloads.filter(d => d.status === 'failed').length}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DownloadHistory;