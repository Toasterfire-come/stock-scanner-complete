import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart, 
  Target,
  ArrowRight,
  Download,
  Calendar,
  BarChart3
} from 'lucide-react';
import { 
  getPortfolioAnalytics, 
  getPortfolioSectorAllocation, 
  getPortfolioDividendTracking,
  exportPortfolioCSV 
} from '../api/client';
import { Link } from 'react-router-dom';
import logger from '../lib/logger';

const EnhancedPortfolioAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [sectorAllocation, setSectorAllocation] = useState(null);
  const [dividendTracking, setDividendTracking] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [analyticsRes, sectorRes, dividendRes] = await Promise.all([
        getPortfolioAnalytics().catch(() => null),
        getPortfolioSectorAllocation().catch(() => null),
        getPortfolioDividendTracking().catch(() => null)
      ]);

      setAnalytics(analyticsRes);
      setSectorAllocation(sectorRes);
      setDividendTracking(dividendRes);
    } catch (err) {
      setError('Failed to load portfolio analytics');
      logger.error('Portfolio analytics error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPortfolio = async () => {
    try {
      const csvData = await exportPortfolioCSV();
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `portfolio-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      logger.error('Export failed:', err);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '$0.00';
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (!value) return '0.00%';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading portfolio analytics...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !analytics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Overview Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Value</CardTitle>
              <DollarSign className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(analytics.total_value)}</div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-muted-foreground">Today:</span>
                <span className={`font-medium ${analytics.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(analytics.day_change)} ({formatPercentage(analytics.day_change_percent)})
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-50 to-green-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Gain/Loss</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${analytics.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(analytics.total_gain_loss)}
              </div>
              <p className="text-xs text-muted-foreground">
                {formatPercentage(analytics.total_gain_loss_percent)} all time
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-50 to-purple-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
              <Target className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.risk_metrics?.concentration_top || 'N/A'}</div>
              <p className="text-xs text-muted-foreground">
                {analytics.risk_metrics?.positions || 0} positions
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-50 to-orange-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Annual Dividends</CardTitle>
              <Calendar className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(dividendTracking?.projection_total || 0)}
              </div>
              <p className="text-xs text-muted-foreground">Projected this year</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Allocation */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Sector Allocation</CardTitle>
              <CardDescription>Your portfolio distribution by sector</CardDescription>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link to="/app/portfolio">
                <PieChart className="h-4 w-4 mr-1" />
                View Details
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {sectorAllocation?.allocation ? (
              <div className="space-y-3">
                {Object.entries(sectorAllocation.allocation).map(([sector, data]) => (
                  <div key={sector} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium">{sector}</div>
                      <div className="text-xs text-gray-600">
                        {data.count} stocks • {formatCurrency(data.value)}
                      </div>
                    </div>
                    <Badge variant="secondary" className="ml-2">
                      {data.percentage.toFixed(1)}%
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8 text-gray-500">
                <div className="text-center">
                  <PieChart className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>No sector allocation data</p>
                  <p className="text-sm">Add stocks to your portfolio</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Dividend Tracking */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Dividend Income</CardTitle>
              <CardDescription>Top dividend-paying holdings</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleExportPortfolio}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </CardHeader>
          <CardContent>
            {dividendTracking?.items?.length > 0 ? (
              <div className="space-y-3">
                {dividendTracking.items.slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex-1">
                      <div className="text-sm font-medium">{item.ticker}</div>
                      <div className="text-xs text-gray-600">
                        {item.shares} shares at {formatCurrency(item.current_price)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {formatCurrency(item.projected_annual_dividend)}
                      </div>
                      <div className="text-xs text-gray-600">
                        {item.dividend_yield?.toFixed(2)}% yield
                      </div>
                    </div>
                  </div>
                ))}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Total Annual Dividend:</span>
                    <span className="text-lg font-bold text-green-600">
                      {formatCurrency(dividendTracking.projection_total)}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center py-8 text-gray-500">
                <div className="text-center">
                  <Target className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>No dividend-paying stocks</p>
                  <p className="text-sm">Add dividend stocks to track income</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Performance Attribution Coming Soon */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Attribution</CardTitle>
          <CardDescription>Detailed breakdown of portfolio performance by sector and individual holdings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-gray-500">
            <div className="text-center">
              <BarChart3 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <p>Performance attribution charts coming soon</p>
              <p className="text-sm">Advanced analytics will show contribution by each holding</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedPortfolioAnalytics;