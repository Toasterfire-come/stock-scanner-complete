import React, { useMemo, useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { TrendingUp, TrendingDown, Eye, Download, RefreshCw, SortAsc, SortDesc, PlusCircle, BellPlus } from "lucide-react";
import { toast } from "sonner";
import { runScreener, getScreener, exportScreenerCsvUrl, addWatchlist, createAlert, getCurrentPlan } from "../../../api/client";
import { trackEvent, trackError } from "../../../lib/telemetry";
import { showError, showSuccess } from "../../../lib/errors";

const ScreenerResults = () => {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [screenerInfo, setScreenerInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [sortBy, setSortBy] = useState({ key: 'change_percent', dir: 'desc' });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [plan, setPlan] = useState({ plan_type: 'free', is_premium: false });

  useEffect(() => { fetchResults(); }, [id]);
  useEffect(() => { (async () => { try { const p = await getCurrentPlan(); const d=p?.data||p||{}; setPlan(d); } catch {} })(); }, []);

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
      showError("Failed to fetch results");
      trackError('screener_results_error', error, { screener_id: id });
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
    if (!plan.is_premium) {
      toast.error('Upgrade required', { description: 'CSV export is available on paid plans.' });
      return;
    }
    const url = exportScreenerCsvUrl(id);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screener-results-${id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showSuccess("Downloading CSV");
    trackEvent('screener_export_csv', { screener_id: id });
  };

  const sorted = useMemo(() => {
    const data = [...results];
    const { key, dir } = sortBy;
    data.sort((a,b) => {
      const va = a[key] ?? 0; const vb = b[key] ?? 0;
      if (va < vb) return dir === 'asc' ? -1 : 1;
      if (va > vb) return dir === 'asc' ? 1 : -1;
      return 0;
    });
    return data;
  }, [results, sortBy]);

  const paged = useMemo(() => {
    const start = (page - 1) * pageSize;
    return sorted.slice(start, start + pageSize);
  }, [sorted, page, pageSize]);

  const changeSort = (key) => {
    setSortBy((prev) => prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'desc' });
  };

  const formatCap = (v) => {
    const n = Number(v || 0);
    if (n >= 1e12) return (n/1e12).toFixed(1) + 'T';
    if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
    if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
    return n.toLocaleString();
  };

  const addToWatchlist = async (ticker) => {
    try { await addWatchlist(ticker); showSuccess('Added to Watchlist'); trackEvent('watchlist_add', { ticker }); }
    catch (e) { showError('Failed to add to Watchlist'); trackError('watchlist_add_error', e, { ticker }); }
  };

  const createPriceAlert = async (ticker) => {
    try { await createAlert({ ticker, target_price: 0, condition: 'above', email: '' }); showSuccess('Alert created'); trackEvent('alert_created', { ticker }); }
    catch (e) { showError('Failed to create alert'); trackError('alert_create_error', e, { ticker }); }
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
                    <TableHead className="sticky top-0 bg-white">Symbol</TableHead>
                    <TableHead className="sticky top-0 bg-white">Company</TableHead>
                    <TableHead className="sticky top-0 bg-white cursor-pointer" onClick={() => changeSort('current_price')}>
                      Price {sortBy.key==='current_price' ? (sortBy.dir==='asc'?<SortAsc className="inline h-3 w-3"/>:<SortDesc className="inline h-3 w-3"/>) : null}
                    </TableHead>
                    <TableHead className="sticky top-0 bg-white cursor-pointer" onClick={() => changeSort('change_percent')}>
                      Change {sortBy.key==='change_percent' ? (sortBy.dir==='asc'?<SortAsc className="inline h-3 w-3"/>:<SortDesc className="inline h-3 w-3"/>) : null}
                    </TableHead>
                    <TableHead className="sticky top-0 bg-white cursor-pointer" onClick={() => changeSort('volume')}>
                      Volume {sortBy.key==='volume' ? (sortBy.dir==='asc'?<SortAsc className="inline h-3 w-3"/>:<SortDesc className="inline h-3 w-3"/>) : null}
                    </TableHead>
                    <TableHead className="sticky top-0 bg-white cursor-pointer" onClick={() => changeSort('market_cap')}>
                      Market Cap {sortBy.key==='market_cap' ? (sortBy.dir==='asc'?<SortAsc className="inline h-3 w-3"/>:<SortDesc className="inline h-3 w-3"/>) : null}
                    </TableHead>
                    <TableHead className="sticky top-0 bg-white">Exchange</TableHead>
                    <TableHead className="sticky top-0 bg-white">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paged.map((stock) => (
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
                      <TableCell>${Number(stock.current_price||0).toFixed(2)}</TableCell>
                      <TableCell>
                        <div className={`flex items-center ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stock.change_percent >= 0 ? (
                            <TrendingUp className="h-4 w-4 mr-1" />
                          ) : (
                            <TrendingDown className="h-4 w-4 mr-1" />
                          )}
                          {stock.change_percent >= 0 ? '+' : ''}{Number(stock.change_percent||0).toFixed(2)}%
                        </div>
                      </TableCell>
                      <TableCell>{Number(stock.volume||0).toLocaleString()}</TableCell>
                      <TableCell>${formatCap(stock.market_cap)}</TableCell>
                      <TableCell>{stock.exchange}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" asChild>
                          <Link to={`/app/stocks/${stock.ticker}`}>
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Link>
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => addToWatchlist(stock.ticker)}>
                            <PlusCircle className="h-4 w-4 mr-1" /> Watchlist
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => createPriceAlert(stock.ticker)}>
                            <BellPlus className="h-4 w-4 mr-1" /> Alert
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">Page {page} of {Math.max(1, Math.ceil(results.length / pageSize))}</div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={page===1} onClick={() => setPage(p => Math.max(1, p-1))}>Prev</Button>
                <Button variant="outline" size="sm" disabled={page*pageSize >= results.length} onClick={() => setPage(p => p+1)}>Next</Button>
                <select className="text-sm border rounded px-2 py-1" value={pageSize} onChange={(e)=>{setPageSize(Number(e.target.value)); setPage(1);}}>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
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