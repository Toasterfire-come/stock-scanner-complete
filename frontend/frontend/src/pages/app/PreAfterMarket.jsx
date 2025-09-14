import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/table";
import { Clock, TrendingUp, TrendingDown, RefreshCw } from "lucide-react";
import { toast } from "sonner";

const PreAfterMarket = () => {
  const [marketData, setMarketData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    fetchMarketData();
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchMarketData = async () => {
    setIsLoading(true);
    try {
      // Simulate pre/after market data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMarketData({
        preMarket: [
          {
            ticker: "AAPL",
            name: "Apple Inc.",
            price: 212.45,
            change: 1.95,
            changePercent: 0.93,
            volume: 245820,
            lastUpdate: "2024-01-15T08:30:00Z"
          },
          {
            ticker: "MSFT", 
            name: "Microsoft Corporation",
            price: 442.10,
            change: 1.80,
            changePercent: 0.41,
            volume: 156742,
            lastUpdate: "2024-01-15T08:29:45Z"
          },
          {
            ticker: "GOOGL",
            name: "Alphabet Inc.",
            price: 138.75,
            change: -0.45,
            changePercent: -0.32,
            volume: 98654,
            lastUpdate: "2024-01-15T08:28:12Z"
          }
        ],
        afterHours: [
          {
            ticker: "NVDA",
            name: "NVIDIA Corporation", 
            price: 129.80,
            change: 1.60,
            changePercent: 1.25,
            volume: 321456,
            lastUpdate: "2024-01-14T20:45:30Z"
          },
          {
            ticker: "TSLA",
            name: "Tesla, Inc.",
            price: 248.90,
            change: -3.20,
            changePercent: -1.27,
            volume: 456789,
            lastUpdate: "2024-01-14T20:42:15Z"
          },
          {
            ticker: "AMZN",
            name: "Amazon.com Inc.",
            price: 152.40,
            change: 2.15,
            changePercent: 1.43,
            volume: 198765,
            lastUpdate: "2024-01-14T20:38:22Z"
          }
        ]
      });
    } catch (error) {
      toast.error("Failed to fetch market data");
    } finally {
      setIsLoading(false);
    }
  };

  const getMarketStatus = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const currentTime = hours * 60 + minutes;
    
    // Market hours: 9:30 AM - 4:00 PM ET (9.5 hours * 60 = 570 minutes to 16*60 = 960 minutes)
    const marketOpen = 9 * 60 + 30; // 9:30 AM
    const marketClose = 16 * 60; // 4:00 PM
    
    if (currentTime >= marketOpen && currentTime < marketClose) {
      return { status: "open", label: "Market Open", color: "bg-green-100 text-green-800" };
    } else if (currentTime < marketOpen) {
      return { status: "premarket", label: "Pre-Market", color: "bg-blue-100 text-blue-800" };
    } else {
      return { status: "afterhours", label: "After Hours", color: "bg-orange-100 text-orange-800" };
    }
  };

  const formatPrice = (price) => `$${price.toFixed(2)}`;
  const formatChange = (change) => `${change >= 0 ? '+' : ''}${change.toFixed(2)}`;
  const formatPercent = (percent) => `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  const formatVolume = (volume) => {
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
    return volume.toString();
  };

  const renderStockTable = (stocks) => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Symbol</TableHead>
          <TableHead>Company</TableHead>
          <TableHead>Price</TableHead>
          <TableHead>Change</TableHead>
          <TableHead>Volume</TableHead>
          <TableHead>Last Update</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {stocks.map((stock) => (
          <TableRow key={stock.ticker}>
            <TableCell className="font-semibold">{stock.ticker}</TableCell>
            <TableCell>{stock.name}</TableCell>
            <TableCell>{formatPrice(stock.price)}</TableCell>
            <TableCell>
              <div className={`flex items-center ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {stock.change >= 0 ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
                <div>
                  <div>{formatChange(stock.change)}</div>
                  <div className="text-xs">{formatPercent(stock.changePercent)}</div>
                </div>
              </div>
            </TableCell>
            <TableCell>{formatVolume(stock.volume)}</TableCell>
            <TableCell className="text-sm text-gray-600">
              {new Date(stock.lastUpdate).toLocaleTimeString()}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  const marketStatus = getMarketStatus();

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pre & After Market</h1>
          <p className="text-gray-600 mt-2">Trading activity outside regular market hours</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge className={marketStatus.color}>
            <Clock className="h-3 w-3 mr-1" />
            {marketStatus.label}
          </Badge>
          <Button onClick={fetchMarketData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Market Status
              <Badge variant="outline">
                {currentTime.toLocaleString()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-600 mb-1">Pre-Market</div>
                <div className="text-lg font-bold text-blue-700">4:00 - 9:30 AM ET</div>
                <div className="text-xs text-blue-600">
                  {marketData?.preMarket?.length || 0} active stocks
                </div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600 mb-1">Regular Hours</div>
                <div className="text-lg font-bold text-green-700">9:30 AM - 4:00 PM ET</div>
                <div className="text-xs text-green-600">
                  {marketStatus.status === 'open' ? 'Currently Open' : 'Closed'}
                </div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-sm text-orange-600 mb-1">After Hours</div>
                <div className="text-lg font-bold text-orange-700">4:00 - 8:00 PM ET</div>
                <div className="text-xs text-orange-600">
                  {marketData?.afterHours?.length || 0} active stocks
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="premarket" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="premarket" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Pre-Market
            </TabsTrigger>
            <TabsTrigger value="afterhours" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              After Hours
            </TabsTrigger>
          </TabsList>

          <TabsContent value="premarket">
            <Card>
              <CardHeader>
                <CardTitle className="text-blue-600">Pre-Market Trading</CardTitle>
              </CardHeader>
              <CardContent>
                {marketData?.preMarket && marketData.preMarket.length > 0 ? (
                  renderStockTable(marketData.preMarket)
                ) : (
                  <div className="text-center py-12">
                    <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <div className="text-gray-500 mb-2">No pre-market activity</div>
                    <div className="text-sm text-gray-400">
                      Pre-market trading occurs between 4:00 AM - 9:30 AM ET
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="afterhours">
            <Card>
              <CardHeader>
                <CardTitle className="text-orange-600">After Hours Trading</CardTitle>
              </CardHeader>
              <CardContent>
                {marketData?.afterHours && marketData.afterHours.length > 0 ? (
                  renderStockTable(marketData.afterHours)
                ) : (
                  <div className="text-center py-12">
                    <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <div className="text-gray-500 mb-2">No after-hours activity</div>
                    <div className="text-sm text-gray-400">
                      After-hours trading occurs between 4:00 PM - 8:00 PM ET
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Card>
          <CardHeader>
            <CardTitle>Important Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <div>
                  <strong>Pre-Market (4:00 AM - 9:30 AM ET):</strong> Limited liquidity and wider spreads. 
                  Prices may differ significantly from regular market hours.
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                <div>
                  <strong>After Hours (4:00 PM - 8:00 PM ET):</strong> Earnings releases and news can cause 
                  significant price movements with lower volume.
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                <div>
                  <strong>Risk Warning:</strong> Extended hours trading involves greater risk due to 
                  reduced liquidity and increased volatility.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PreAfterMarket;