import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { TrendingUp, TrendingDown, Eye, Download, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { filterStocks, runScreener } from "../../../api/client";
import { 
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis
} from "../../../components/ui/pagination";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";

const ScreenerResults = () => {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [screenerInfo, setScreenerInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchResults();
  }, [id, page, pageSize]);

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      let data;
      let baseParams = {};
      if (id === 'adhoc') {
        const stored = window.localStorage.getItem('screener:lastParams');
        baseParams = stored ? JSON.parse(stored) : {};
        const requestParams = { ...baseParams };
        requestParams.limit = pageSize;
        requestParams.offset = (page - 1) * pageSize;
        requestParams.page = page;
        requestParams.page_size = pageSize;
        data = await filterStocks(requestParams);
      } else {
        // Use backend screener results endpoint for saved screeners
        const res = await runScreener(id);
        data = res;
      }
      const rows = Array.isArray(data?.stocks)
        ? data.stocks
        : (Array.isArray(data?.results)
          ? data.results
          : (Array.isArray(data?.data?.results)
            ? data.data.results
            : (Array.isArray(data) ? data : [])));

      const total = Number(
        data?.total_count ?? data?.totalCount ?? data?.count ?? data?.data?.total_count ?? rows.length
      );
      setTotalCount(Number.isFinite(total) ? total : rows.length);

      // Basic info
      setScreenerInfo({
        name: id === 'adhoc' ? 'Ad-hoc Screener' : `Screener ${id}`,
        description: id === 'adhoc' ? 'Results from custom filter' : 'Results from saved screener',
        lastRun: new Date().toISOString(),
        criteria: id === 'adhoc' ? Object.keys(baseParams || {}).map(k => `${k}=${baseParams[k]}`) : []
      });

      setResults(rows.map((s) => ({
        ticker: s.ticker || s.symbol,
        company_name: s.company_name || s.name || '-',
        current_price: Number(s.current_price ?? s.price ?? 0),
        change_percent: Number(
          s.change_percent ?? s.price_change_percent ?? s.change ?? s.price_change ?? 0
        ),
        volume: Number(s.volume ?? 0),
        market_cap: Number(s.market_cap ?? 0),
        exchange: s.exchange || '-'
      })));
    } catch (error) {
      toast.error("Failed to fetch results");
      setResults([]);
    } finally {
      setIsLoading(false);
    }
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
    const csv = [
      "Ticker,Company,Price,Change %,Volume,Market Cap,Exchange",
      ...results.map(stock => 
        `${stock.ticker},${stock.company_name},${stock.current_price},${stock.change_percent},${stock.volume},${stock.market_cap},${stock.exchange}`
      )
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `screener-results-${id}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success("Results exported to CSV");
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
                <div className="text-2xl font-bold text-blue-600">{totalCount}</div>
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
                  {results.length > 0
                    ? `${((results.reduce((sum, stock) => sum + (Number(stock.change_percent)||0), 0) / results.length).toFixed(2))}%`
                    : '0.00%'}
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
                    <TableRow key={stock.ticker} className="odd:bg-white even:bg-gray-50">
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
                      <TableCell>{Number(stock.volume||0).toLocaleString()}</TableCell>
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

        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">Page {page} of {Math.max(1, Math.ceil(totalCount / pageSize))}</div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Rows per page</span>
              <Select value={String(pageSize)} onValueChange={(v) => { setPageSize(Number(v)); setPage(1); }}>
                <SelectTrigger className="w-24">
                  <SelectValue placeholder={String(pageSize)} />
                </SelectTrigger>
                <SelectContent>
                  {[25, 50, 100, 250].map(sz => (
                    <SelectItem key={sz} value={String(sz)}>{sz}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious onClick={(e) => { e.preventDefault(); if (page > 1) setPage(page - 1); }} href="#" />
                </PaginationItem>
                <PaginationItem>
                  <PaginationLink isActive href="#">{page}</PaginationLink>
                </PaginationItem>
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
                <PaginationItem>
                  <PaginationNext onClick={(e) => { e.preventDefault(); const maxPage = Math.max(1, Math.ceil(totalCount / pageSize)); if (page < maxPage) setPage(page + 1); }} href="#" />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScreenerResults;