import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { ArrowLeft, Download, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import logger from '../../../lib/logger';

const EnhancedScreenerResults = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [filters, setFilters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = () => {
    try {
      const resultsData = sessionStorage.getItem('screener_results');
      const filtersData = sessionStorage.getItem('screener_filters');
      
      if (resultsData) {
        setResults(JSON.parse(resultsData));
      }
      if (filtersData) {
        setFilters(JSON.parse(filtersData));
      }
    } catch (error) {
      logger.error('Failed to load results:', error);
      toast.error('Failed to load results');
    }
  };

  const formatValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
      if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
      if (Math.abs(value) >= 1e3) return value.toFixed(0).toLocaleString();
      if (value < 1 && value > 0) return value.toFixed(4);
      return value.toFixed(2);
    }
    return value.toString();
  };

  const exportToCSV = () => {
    if (!results?.results || results.results.length === 0) {
      toast.error('No results to export');
      return;
    }

    const data = results.results;
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          if (value === null || value === undefined) return '';
          if (typeof value === 'string' && value.includes(',')) return `"${value}"`;
          return value;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screener_results_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Results exported to CSV');
  };

  const getDisplayColumns = () => {
    if (!results?.results || results.results.length === 0) return [];
    
    const sample = results.results[0];
    const priorityColumns = [
      'ticker',
      'company_name',
      'current_price',
      'price_change_percent',
      'volume',
      'market_cap',
      'pe_ratio',
      'valuation_score',
      'strength_score',
      'sector'
    ];

    const availableColumns = Object.keys(sample);
    const displayColumns = [];

    // Add priority columns first if they exist
    priorityColumns.forEach(col => {
      if (availableColumns.includes(col)) {
        displayColumns.push(col);
      }
    });

    // Add remaining columns
    availableColumns.forEach(col => {
      if (!displayColumns.includes(col)) {
        displayColumns.push(col);
      }
    });

    return displayColumns.slice(0, 12); // Limit to 12 columns for readability
  };

  const getColumnLabel = (column) => {
    const labels = {
      ticker: 'Ticker',
      company_name: 'Company',
      current_price: 'Price',
      price_change_percent: 'Change %',
      volume: 'Volume',
      market_cap: 'Market Cap',
      pe_ratio: 'P/E',
      forward_pe: 'Fwd P/E',
      peg_ratio: 'PEG',
      price_to_book: 'P/B',
      gross_margin: 'Gross Margin',
      operating_margin: 'Op Margin',
      profit_margin: 'Profit Margin',
      roe: 'ROE',
      roa: 'ROA',
      revenue_growth_yoy: 'Rev Growth',
      earnings_growth_yoy: 'EPS Growth',
      current_ratio: 'Current Ratio',
      debt_to_equity: 'D/E',
      dcf_value: 'DCF Value',
      graham_number: 'Graham #',
      valuation_score: 'Val Score',
      valuation_status: 'Status',
      strength_score: 'Strength',
      strength_grade: 'Grade',
      sector: 'Sector',
      industry: 'Industry',
      exchange: 'Exchange'
    };
    return labels[column] || column.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!results) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-gray-600">No results found</p>
            <Button className="mt-4" onClick={() => navigate('/app/screeners/new')}>
              Create New Screener
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const columns = getDisplayColumns();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={() => navigate('/app/screeners/new')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Screener Results</h1>
              <p className="text-gray-600 mt-1">
                Found {results.results?.length || 0} stocks matching your criteria
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={exportToCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Active Filters Summary */}
        {filters.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Active Filters ({filters.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {filters.map((filter, idx) => (
                  <Badge key={idx} variant="secondary">
                    {filter.label}: {filter.operator} {filter.value}
                    {filter.value2 ? ` - ${filter.value2}` : ''}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Table */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Results</CardTitle>
              {results.pagination && (
                <div className="text-sm text-gray-500">
                  Page {results.pagination.page} of {results.pagination.total_pages} 
                  ({results.pagination.total_count} total)
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    {columns.map((col) => (
                      <th key={col} className="text-left p-3 font-medium text-sm text-gray-700">
                        {getColumnLabel(col)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.results && results.results.length > 0 ? (
                    results.results.map((stock, idx) => (
                      <tr 
                        key={idx} 
                        className="border-b hover:bg-gray-50 cursor-pointer"
                        onClick={() => navigate(`/app/stocks/${stock.ticker}`)}
                      >
                        {columns.map((col) => (
                          <td key={col} className="p-3 text-sm">
                            {col === 'ticker' ? (
                              <span className="font-medium text-blue-600">{stock[col]}</span>
                            ) : col === 'company_name' ? (
                              <span className="font-medium">{stock[col]}</span>
                            ) : col === 'price_change_percent' ? (
                              <span className={stock[col] >= 0 ? 'text-green-600' : 'text-red-600'}>
                                {stock[col] !== null && stock[col] !== undefined ? `${stock[col] > 0 ? '+' : ''}${stock[col].toFixed(2)}%` : 'N/A'}
                              </span>
                            ) : col === 'valuation_status' ? (
                              <Badge variant={
                                stock[col]?.includes('undervalued') ? 'success' :
                                stock[col]?.includes('overvalued') ? 'destructive' :
                                'secondary'
                              }>
                                {stock[col] || 'N/A'}
                              </Badge>
                            ) : col === 'strength_grade' ? (
                              <Badge variant={
                                ['A', 'B'].includes(stock[col]) ? 'success' :
                                ['C'].includes(stock[col]) ? 'secondary' :
                                'destructive'
                              }>
                                {stock[col] || 'N/A'}
                              </Badge>
                            ) : (
                              formatValue(stock[col])
                            )}
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={columns.length} className="p-8 text-center text-gray-500">
                        No stocks found matching your criteria
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Pagination Info */}
        {results.pagination && results.pagination.total_pages > 1 && (
          <div className="mt-4 text-center text-sm text-gray-500">
            <p>Showing page {results.pagination.page} of {results.pagination.total_pages}</p>
            <p className="mt-1">Use the API to fetch additional pages programmatically</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedScreenerResults;
