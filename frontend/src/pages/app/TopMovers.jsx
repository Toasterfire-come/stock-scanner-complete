import React, { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { TrendingUp, TrendingDown, Volume2, RefreshCw, Eye, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { getTrendingSafe } from "../../api/client";
import VirtualizedList from "../../components/VirtualizedList";

const TopMovers = () => {
  const [trendingData, setTrendingData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState("");
  const [page, setPage] = useState({ gainers: 1, losers: 1, volume: 1 });
  const pageSize = 50;

  useEffect(() => { fetchTrendingData(); }, []);

  const fetchTrendingData = async () => {
    setIsLoading(true); setError("");
    try {
      const res = await getTrendingSafe();
      if (!res.success) { setError(res.error); toast.error(res.error); }
      setTrendingData(res.data); setLastUpdated(new Date());
    } catch (error) { const msg = "Failed to fetch trending data"; setError(msg); toast.error(msg); }
    finally { setIsLoading(false); }
  };

  const lists = {
    gainers: useMemo(() => trendingData?.top_gainers || [], [trendingData]),
    losers: useMemo(() => (trendingData?.top_losers && trendingData.top_losers.length ? trendingData.top_losers : (trendingData?.top_gainers || []).map(s => ({ ...s, change_percent: -Math.abs(s.change_percent) })).sort((a,b)=>a.change_percent-b.change_percent)), [trendingData]),
    volume: useMemo(() => trendingData?.high_volume || [], [trendingData])
  };

  const totalPages = {
    gainers: Math.max(1, Math.ceil(lists.gainers.length / pageSize)),
    losers: Math.max(1, Math.ceil(lists.losers.length / pageSize)),
    volume: Math.max(1, Math.ceil(lists.volume.length / pageSize))
  };

  const slice = (arr, key) => arr.slice((page[key]-1)*pageSize, page[key]*pageSize);
  const useVirtual = (arr) => arr.length > 200;

  const formatChange = (v) => { const n = Number(v); if (!Number.isFinite(n)) return '-'; return `${n>=0?'+':''}${n.toFixed(2)}%`; };
  const formatPrice = (v) => { const n = Number(v); if (!Number.isFinite(n)) return '-'; return `$${n.toFixed(2)}`; };
  const formatVolume = (v) => { const n = Number(v); if (!Number.isFinite(n)) return '-'; if (n>=1e9) return `${(n/1e9).toFixed(1)}B`; if (n>=1e6) return `${(n/1e6).toFixed(1)}M`; if (n>=1e3) return `${(n/1e3).toFixed(1)}K`; return n.toString(); };
  const formatMarketCap = (v) => { const n = Number(v); if (!Number.isFinite(n)) return '-'; if (n>=1e12) return `$${(n/1e12).toFixed(1)}T`; if (n>=1e9) return `$${(n/1e9).toFixed(1)}B`; if (n>=1e6) return `$${(n/1e6).toFixed(1)}M`; return `$${n}`; };

  const renderRow = (stock) => (
    <tr key={stock.ticker} className="border-b">
      <TableCell>
        <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
      </TableCell>
      <TableCell className="font-medium">{stock.name}</TableCell>
      <TableCell>{formatPrice(stock.current_price)}</TableCell>
      <TableCell>
        <div className={`flex items-center ${Number(stock.change_percent) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {Number(stock.change_percent) >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
          {formatChange(stock.change_percent)}
        </div>
      </TableCell>
      <TableCell>
        <div className="flex items-center">
          <Volume2 className="h-4 w-4 mr-1 text-gray-400" />
          {formatVolume(stock.volume)}
        </div>
      </TableCell>
      <TableCell>{formatMarketCap(stock.market_cap)}</TableCell>
      <TableCell>
        <Button size="sm" variant="outline" asChild>
          <Link to={`/app/stocks/${stock.ticker}`}>
            <Eye className="h-4 w-4 mr-1" /> View
          </Link>
        </Button>
      </TableCell>
    </tr>
  );

  const renderTable = (arrKey, showVolume=false) => {
    const data = lists[arrKey];
    const currentSlice = slice(data, arrKey);
    const isVirt = useVirtual(currentSlice);

    if (isVirt) {
      return (
        <div className="border rounded">
          <div className="grid grid-cols-6 text-sm font-medium text-muted-foreground px-4 py-2 border-b">
            <div>Symbol</div><div>Company</div><div>Price</div><div>Change</div><div>Volume</div><div>Market Cap</div>
          </div>
          <VirtualizedList
            items={currentSlice}
            height={560}
            itemSize={56}
            row={({ item, style }) => (
              <div style={{...style}} className="grid grid-cols-6 items-center px-4 border-b">
                <div><Link to={`/app/stocks/${item.ticker}`} className="font-semibold text-blue-600 hover:underline">{item.ticker}</Link></div>
                <div className="font-medium truncate">{item.name}</div>
                <div>{formatPrice(item.current_price)}</div>
                <div className={`${Number(item.change_percent)>=0?'text-green-600':'text-red-600'}`}>{formatChange(item.change_percent)}</div>
                <div className="text-muted-foreground">{formatVolume(item.volume)}</div>
                <div>{formatMarketCap(item.market_cap)}</div>
              </div>
            )}
          />
        </div>
      );
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Symbol</TableHead>
            <TableHead>Company</TableHead>
            <TableHead>Price</TableHead>
            <TableHead>Change</TableHead>
            {showVolume && <TableHead>Volume</TableHead>}
            <TableHead>Market Cap</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {currentSlice.length ? currentSlice.map((stock) => (
            <TableRow key={stock.ticker}>
              <TableCell>
                <Link to={`/app/stocks/${stock.ticker}`} className="font-semibold text-blue-600 hover:underline">{stock.ticker}</Link>
              </TableCell>
              <TableCell className="font-medium">{stock.name}</TableCell>
              <TableCell>{formatPrice(stock.current_price)}</TableCell>
              <TableCell>
                <div className={`flex items-center ${Number(stock.change_percent) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {Number(stock.change_percent) >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                  {formatChange(stock.change_percent)}
                </div>
              </TableCell>
              {showVolume && (
                <TableCell>
                  <div className="flex items-center">
                    <Volume2 className="h-4 w-4 mr-1 text-gray-400" />
                    {formatVolume(stock.volume)}
                  </div>
                </TableCell>
              )}
              <TableCell>{formatMarketCap(stock.market_cap)}</TableCell>
              <TableCell>
                <Button size="sm" variant="outline" asChild>
                  <Link to={`/app/stocks/${stock.ticker}`}>
                    <Eye className="h-4 w-4 mr-1" /> View
                  </Link>
                </Button>
              </TableCell>
            </TableRow>
          )) : (
            <TableRow><TableCell colSpan={7} className="text-center text-gray-500">No data available</TableCell></TableRow>
          )}
        </TableBody>
      </Table>
    );
  };

  const Paginator = ({ k }) => (
    totalPages[k] > 1 ? (
      <div className="flex items-center justify-between mt-4">
        <div className="text-sm text-muted-foreground">Page {page[k]} of {totalPages[k]}</div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => setPage(p=>({ ...p, [k]: Math.max(1, p[k]-1) }))} disabled={page[k]===1}>Previous</Button>
          <div className="flex gap-1">
            {Array.from({ length: Math.min(totalPages[k], 5) }, (_, i) => { const pg = Math.max(1, page[k]-2) + i; if (pg>totalPages[k]) return null; return (<Button key={pg} variant={pg===page[k]?"default":"outline"} size="sm" onClick={()=>setPage(p=>({ ...p, [k]: pg }))}>{pg}</Button>); })}
          </div>
          <Button size="sm" variant="outline" onClick={() => setPage(p=>({ ...p, [k]: Math.min(totalPages[k], p[k]+1) }))} disabled={page[k]===totalPages[k]}>Next</Button>
        </div>
      </div>
    ) : null
  );

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8"><div className="animate-pulse space-y-4"><div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-1/3"></div><div className="h-12 bg-gray-200 dark:bg-gray-800 rounded"></div><div className="h-96 bg-gray-200 dark:bg-gray-800 rounded"></div></div></div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Top Movers</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Stocks with the highest price movements and volume</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant="outline">{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}</Badge>
          <Button onClick={fetchTrendingData} variant="outline"><RefreshCw className="h-4 w-4 mr-2" /> Refresh</Button>
        </div>
      </div>

      {error && (
        <Card className="border-l-4 border-l-yellow-500 bg-yellow-50/50 dark:bg-yellow-900/20 mb-6"><CardContent className="p-4 text-yellow-800 dark:text-yellow-300 flex items-center justify-between"><span className="flex items-center gap-2"><AlertTriangle className="h-4 w-4" /> {error}</span><Button size="sm" variant="outline" onClick={fetchTrendingData}>Retry</Button></CardContent></Card>
      )}

      <Tabs defaultValue="gainers" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="gainers" className="flex items-center gap-2"><TrendingUp className="h-4 w-4" /> Top Gainers</TabsTrigger>
          <TabsTrigger value="losers" className="flex items-center gap-2"><TrendingDown className="h-4 w-4" /> Top Losers</TabsTrigger>
          <TabsTrigger value="volume" className="flex items-center gap-2"><Volume2 className="h-4 w-4" /> Most Active</TabsTrigger>
        </TabsList>

        <TabsContent value="gainers">
          <Card><CardHeader><CardTitle className="flex items-center gap-2 text-green-600"><TrendingUp className="h-5 w-5" /> Top Gainers</CardTitle></CardHeader><CardContent>{renderTable('gainers', true)}<Paginator k="gainers" /></CardContent></Card>
        </TabsContent>
        <TabsContent value="losers">
          <Card><CardHeader><CardTitle className="flex items-center gap-2 text-red-600"><TrendingDown className="h-5 w-5" /> Top Losers</CardTitle></CardHeader><CardContent>{renderTable('losers', true)}<Paginator k="losers" /></CardContent></Card>
        </TabsContent>
        <TabsContent value="volume">
          <Card><CardHeader><CardTitle className="flex items-center gap-2 text-blue-600"><Volume2 className="h-5 w-5" /> Most Active by Volume</CardTitle></CardHeader><CardContent>{renderTable('volume', true)}<Paginator k="volume" /></CardContent></Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TopMovers;