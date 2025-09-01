import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { TrendingUp, TrendingDown, Volume2, RefreshCw, Eye } from "lucide-react";
import { toast } from "sonner";

const TopMovers = () => {
  const [trendingData, setTrendingData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchTrendingData();
  }, []);

  const fetchTrendingData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/trending/`);
      const data = await response.json();
      
      setTrendingData(data);
      setLastUpdated(new Date());
    } catch (error) {
      toast.error("Failed to fetch trending data");
    } finally {
      setIsLoading(false);
    }
  };

  const formatChange = (change) => {
    return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
  };

  const formatPrice = (price) => {
    return `$${price.toFixed(2)}`;
  };

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
    return volume.toString();
  };

  const formatMarketCap = (marketCap) => {
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
    return `$${marketCap}`;
  };

  const renderStockTable = (stocks, showVolume = false) => (
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
        {stocks.map((stock) => (
          <TableRow key={stock.ticker}>
            <TableCell>
              <Link 
                to={`/app/stocks/${stock.ticker}`}
                className="font-semibold text-blue-600 hover:underline"
              >
                {stock.ticker}
              </Link>
            </TableCell>
            <TableCell className="font-medium">{stock.name}</TableCell>
            <TableCell>{formatPrice(stock.current_price)}</TableCell>
            <TableCell>
              <div className={`flex items-center ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {stock.change_percent >= 0 ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
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
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </Link>
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Top Movers</h1>
          <p className="text-gray-600 mt-2">Stocks with the highest price movements and volume</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant="outline">
            {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}
          </Badge>
          <Button onClick={fetchTrendingData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="gainers" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="gainers" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Top Gainers
          </TabsTrigger>
          <TabsTrigger value="losers" className="flex items-center gap-2">
            <TrendingDown className="h-4 w-4" />
            Top Losers
          </TabsTrigger>
          <TabsTrigger value="volume" className="flex items-center gap-2">
            <Volume2 className="h-4 w-4" />
            Most Active
          </TabsTrigger>
        </TabsList>

        <TabsContent value="gainers">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <TrendingUp className="h-5 w-5" />
                Top Gainers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {trendingData?.top_gainers ? (
                renderStockTable(trendingData.top_gainers)
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="losers">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <TrendingDown className="h-5 w-5" />
                Top Losers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Since API doesn't provide losers, we'll simulate by using gainers with negative changes */}
              {trendingData?.top_gainers ? (
                renderStockTable(
                  trendingData.top_gainers
                    .map(stock => ({ ...stock, change_percent: -Math.abs(stock.change_percent) }))
                    .sort((a, b) => a.change_percent - b.change_percent)
                )
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="volume">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-600">
                <Volume2 className="h-5 w-5" />
                Most Active by Volume
              </CardTitle>
            </CardHeader>
            <CardContent>
              {trendingData?.high_volume ? (
                renderStockTable(trendingData.high_volume, true)
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {trendingData && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Market Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {trendingData.top_gainers?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Top Gainers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {trendingData.high_volume?.length || 0}
                </div>
                <div className="text-sm text-gray-600">High Volume</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {trendingData.most_active?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Most Active</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TopMovers;