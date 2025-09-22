import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Badge } from "../../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { TrendingUp, TrendingDown, Eye, Download, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { getScreener, runScreener } from "../../../api/client";

const ScreenerDetail = () => {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [screenerInfo, setScreenerInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [id]);

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      const [info, res] = await Promise.all([
        id && id !== 'adhoc' ? getScreener(id).catch(() => null) : Promise.resolve(null),
        id && id !== 'adhoc' ? runScreener(id).catch(() => ({ stocks: [], total_count: 0 })) : Promise.resolve({ stocks: [], total_count: 0 })
      ]);

      const screenerName = info?.data?.name || (id === 'adhoc' ? 'Ad-hoc Screener' : `Screener ${id}`);
      const criteriaArr = Array.isArray(info?.data?.criteria)
        ? info.data.criteria.map((c) => typeof c === 'string' ? c : JSON.stringify(c))
        : [];

      setScreenerInfo({
        name: screenerName,
        description: info?.data?.description || '',
        lastRun: new Date().toISOString(),
        criteria: criteriaArr,
      });

      const rows = Array.isArray(res?.stocks) ? res.stocks : [];
      setResults(rows.map((s) => ({
        ticker: s.ticker || s.symbol,
        company_name: s.company_name || s.name || '-',
        current_price: Number(s.current_price || s.price || 0),
        change_percent: Number(s.price_change_percent || s.change_percent || s.change || 0),
        volume: Number(s.volume || 0),
        market_cap: Number(s.market_cap || 0),
        exchange: s.exchange || '-'
      })));
    } catch (error) {
      toast.error("Failed to load screener results");
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
    } catch {
      toast.error("Failed to refresh");
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
    a.download = `screener-${id}-results.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success("Exported");
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
          <h1 className="text-3xl font-bold text-gray-900">{screenerInfo?.name}</h1>
          {screenerInfo?.description && (
            <p className="text-gray-600 mt-2">{screenerInfo.description}</p>
          )}
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
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            {screenerInfo?.criteria && screenerInfo.criteria.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {screenerInfo.criteria.map((c, i) => (
                  <Badge key={i} variant="outline">{c}</Badge>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-500">No filters defined</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
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
                    <TableRow key={stock.ticker} className="odd:bg-gray-50">
                      <TableCell>
                        <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">
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
              <div className="text-center py-12 text-gray-500">No stocks match your filters.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ScreenerDetail;

