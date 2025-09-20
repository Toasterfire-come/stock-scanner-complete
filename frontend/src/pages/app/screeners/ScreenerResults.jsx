import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { TrendingUp, TrendingDown, Eye, Download, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { runScreener, getScreener, exportScreenerCsvUrl } from "../../../api/client";

const ScreenerResults = () => {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [screenerInfo, setScreenerInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => { fetchResults(); }, [id]);

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      const [meta, res] = await Promise.all([
        getScreener(id).catch(() => ({})),
        runScreener(id, { limit: 200 }).catch(() => ({}))
      ]);
      const info = meta?.data || meta || {};
      setScreenerInfo({
        name: info.name || 'Untitled Screener',
        description: info.description || '',
        lastRun: info.last_run || null,
        criteria: Array.isArray(info.criteria) ? info.criteria.map(c => c.name || c.id || 'Criterion') : []
      });
      const items = res?.data?.results || res?.results || res?.data || [];
      setResults(Array.isArray(items) ? items : []);
    } catch (error) {
      toast.error("Failed to fetch results");
      setScreenerInfo(null);
      setResults([]);
    } finally { setIsLoading(false); }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await fetchResults();
      toast.success("Results refreshed");
    } catch (error) {
      toast.error("Failed to refresh results");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleExport = () => {
    // Use backend CSV export for consistency
    const url = exportScreenerCsvUrl(id);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screener-results-${id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    toast.success("Downloading CSV");
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Screener Results</h1>
          <p className="text-gray-600 mt-2">{screenerInfo?.name}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Screener Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-500">Total Results</div>
                <div className="text-2xl font-bold text-blue-600">{results.length}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Last Updated</div>
                <div className="text-sm font-medium">
                  {screenerInfo?.lastRun ? new Date(screenerInfo.lastRun).toLocaleString() : 'Never'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Criteria Count</div>
                <div className="text-2xl font-bold">{screenerInfo?.criteria?.length || 0}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Avg. Price Change</div>
                <div className="text-2xl font-bold text-green-600">
                  +{(results.reduce((sum, stock) => sum + stock.change_percent, 0) / results.length).toFixed(2)}%
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="text-sm text-gray-500 mb-2">Active Criteria:</div>
              <div className="flex flex-wrap gap-2">
                {screenerInfo?.criteria?.map((criterion, index) => (
                  <Badge key={index} variant="outline">{criterion}</Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Matching Stocks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Change</TableHead>
                    <TableHead>Volume</TableHead>
                    <TableHead>Market Cap</TableHead>
                    <TableHead>Exchange</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((stock) => (
                    <TableRow key={stock.ticker}>
                      <TableCell>
                        <Link 
                          to={`/app/stocks/${stock.ticker}`}
                          className="font-semibold text-blue-600 hover:underline"
                        >
                          {stock.ticker}
                        </Link>
                      </TableCell>
                      <TableCell className="font-medium">{stock.company_name}</TableCell>
                      <TableCell>${stock.current_price.toFixed(2)}</TableCell>
                      <TableCell>
                        <div className={`flex items-center ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stock.change_percent >= 0 ? (
                            <TrendingUp className="h-4 w-4 mr-1" />
                          ) : (
                            <TrendingDown className="h-4 w-4 mr-1" />
                          )}
                          {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                        </div>
                      </TableCell>
                      <TableCell>{stock.volume.toLocaleString()}</TableCell>
                      <TableCell>${(stock.market_cap / 1e9).toFixed(1)}B</TableCell>
                      <TableCell>{stock.exchange}</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline" asChild>
                          <Link to={`/app/stocks/${stock.ticker}`}>
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {results.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">No stocks match your criteria</div>
                <Button asChild>
                  <Link to={`/app/screeners/${id}/edit`}>Adjust Criteria</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ScreenerResults;