import React, { useState, useEffect } from "react";
import SEO from "../../components/SEO";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Skeleton } from "../../components/ui/skeleton";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { 
  ArrowLeft,
  Star,
  Bell,
  Share2,
  Download,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Volume2,
  DollarSign,
  Target,
  Building,
  Calendar,
  Globe,
  Users,
  BarChart3,
  Activity,
  Sparkles,
} from "lucide-react";
import EnhancedStockChart from "../../components/EnhancedStockChart";
import StockMetricsComparison from "../../components/StockMetricsComparison";
import { cn } from "../../lib/utils";
import logger from '../../lib/logger';

// Client-side Yahoo Finance quote fetcher
const fetchYahooQuote = async (symbol) => {
  try {
    const response = await fetch(
      `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${symbol}?modules=price,summaryDetail,defaultKeyStatistics,financialData,assetProfile`,
      { method: 'GET', headers: { 'User-Agent': 'Mozilla/5.0' } }
    );
    const data = await response.json();
    
    if (data.quoteSummary?.result?.[0]) {
      const result = data.quoteSummary.result[0];
      const price = result.price || {};
      const summary = result.summaryDetail || {};
      const stats = result.defaultKeyStatistics || {};
      const financial = result.financialData || {};
      const profile = result.assetProfile || {};
      
      return {
        ticker: symbol,
        company_name: price.longName || price.shortName || symbol,
        current_price: price.regularMarketPrice?.raw || 0,
        price_change_today: price.regularMarketChange?.raw || 0,
        change_percent: price.regularMarketChangePercent?.raw * 100 || 0,
        market_cap: price.marketCap?.raw || 0,
        volume: summary.volume?.raw || 0,
        avg_volume_3mon: summary.averageVolume?.raw || 0,
        pe_ratio: summary.trailingPE?.raw || 0,
        forward_pe: summary.forwardPE?.raw || 0,
        earnings_per_share: stats.trailingEps?.raw || 0,
        dividend_yield: summary.dividendYield?.raw * 100 || 0,
        days_high: price.regularMarketDayHigh?.raw || 0,
        days_low: price.regularMarketDayLow?.raw || 0,
        fifty_two_week_high: summary.fiftyTwoWeekHigh?.raw || 0,
        fifty_two_week_low: summary.fiftyTwoWeekLow?.raw || 0,
        exchange: price.exchangeName || 'N/A',
        currency: price.currency || 'USD',
        sector: profile.sector || 'N/A',
        industry: profile.industry || 'N/A',
        website: profile.website || '',
        employees: profile.fullTimeEmployees || 0,
        description: profile.longBusinessSummary || '',
        target_price: financial.targetMeanPrice?.raw || 0,
        recommendation: financial.recommendationKey || 'none',
        revenue_growth: financial.revenueGrowth?.raw * 100 || 0,
        profit_margin: financial.profitMargins?.raw * 100 || 0,
        beta: summary.beta?.raw || 0,
        book_value: stats.bookValue?.raw || 0,
        price_to_book: stats.priceToBook?.raw || 0,
        last_updated: new Date().toISOString(),
      };
    }
    return null;
  } catch (error) {
    logger.error('Failed to fetch quote:', error);
    return null;
  }
};

const EnhancedStockDetail = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [stockData, setStockData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    const fetchData = async () => {
      if (!symbol) return;
      
      setIsLoading(true);
      try {
        const data = await fetchYahooQuote(symbol.toUpperCase());
        
        if (data) {
          setStockData(data);
        } else {
          toast.error('Failed to load stock data');
        }
      } catch (error) {
        toast.error('Error fetching stock data');
        logger.error(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [symbol]);

  const handleShare = async () => {
    const url = window.location.href;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${stockData.ticker} - ${stockData.company_name}`,
          text: `Check out ${stockData.company_name} stock analysis`,
          url,
        });
      } catch (error) {
        // User cancelled or error
      }
    } else {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(url);
      toast.success('Link copied to clipboard!');
    }
  };

  const formatCurrency = (value) => {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const formatLargeNumber = (value) => {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return '0';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(0)}K`;
    return num.toLocaleString();
  };

  const formatVolume = (value) => {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return '0';
    if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(0)}K`;
    return num.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-6">
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-96 w-full" />
          <div className="grid md:grid-cols-3 gap-6">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <SEO title={`Stock Not Found | Trade Scan Pro`} robots="noindex,follow" />
        <Alert variant="destructive">
          <AlertDescription>
            Unable to load stock data for "{symbol}". Please check the symbol and try again.
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/app/stocks')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Stocks
        </Button>
      </div>
    );
  }

  const isPositive = stockData.change_percent >= 0;
  
  // Create valuation data for comparison
  const valuationData = {
    fair_value_restricted: {
      base: stockData.target_price || stockData.current_price * 1.1,
    },
    analyst_target: stockData.target_price,
    subsector_pe_base: 15, // Default sector PE
    forward_eps: stockData.earnings_per_share,
    sector: stockData.sector,
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <SEO
        title={`${stockData.ticker} - ${stockData.company_name} | Live Stock Analysis`}
        description={`Real-time stock analysis for ${stockData.company_name} (${stockData.ticker}). View live charts, key metrics, and valuation analysis.`}
        url={process.env.REACT_APP_PUBLIC_URL ? `${process.env.REACT_APP_PUBLIC_URL}/app/stocks/${encodeURIComponent(stockData.ticker)}` : `https://tradescanpro.com/app/stocks/${encodeURIComponent(stockData.ticker)}`}
      />
      
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/app/stocks')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Stocks
          </Button>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleShare}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href={`https://finance.yahoo.com/quote/${symbol}`} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Yahoo Finance
              </a>
            </Button>
          </div>
        </div>

        {/* Stock Header Card */}
        <Card className="border-2 bg-gradient-to-r from-blue-50 via-white to-purple-50">
          <CardContent className="p-6">
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-4xl font-bold">{stockData.ticker}</h1>
                  <Badge variant="outline" className="text-sm">
                    {stockData.exchange}
                  </Badge>
                  {stockData.recommendation && stockData.recommendation !== 'none' && (
                    <Badge variant="secondary" className="capitalize">
                      {stockData.recommendation}
                    </Badge>
                  )}
                </div>
                <h2 className="text-xl text-muted-foreground">{stockData.company_name}</h2>
                
                {stockData.sector && (
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Building className="h-4 w-4" />
                      {stockData.sector}
                    </div>
                    {stockData.industry && (
                      <div className="flex items-center gap-1">
                        <BarChart3 className="h-4 w-4" />
                        {stockData.industry}
                      </div>
                    )}
                    {stockData.employees > 0 && (
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {stockData.employees.toLocaleString()} employees
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div className="text-right space-y-2">
                <div className="text-5xl font-bold">
                  {formatCurrency(stockData.current_price)}
                </div>
                <div className={cn(
                  'flex items-center justify-end gap-2 text-xl font-semibold',
                  isPositive ? 'text-green-600' : 'text-red-600'
                )}>
                  {isPositive ? <TrendingUp className="h-6 w-6" /> : <TrendingDown className="h-6 w-6" />}
                  {isPositive ? '+' : ''}{formatCurrency(stockData.price_change_today)}
                  <span className="text-lg">
                    ({isPositive ? '+' : ''}{stockData.change_percent.toFixed(2)}%)
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  As of {new Date(stockData.last_updated).toLocaleTimeString()}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-700 font-medium">Market Cap</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {formatLargeNumber(stockData.market_cap)}
                  </p>
                </div>
                <Building className="h-10 w-10 text-blue-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700 font-medium">Volume</p>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {formatVolume(stockData.volume)}
                  </p>
                </div>
                <Volume2 className="h-10 w-10 text-green-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-700 font-medium">P/E Ratio</p>
                  <p className="text-2xl font-bold text-purple-600 mt-1">
                    {stockData.pe_ratio > 0 ? stockData.pe_ratio.toFixed(2) : 'N/A'}
                  </p>
                </div>
                <Target className="h-10 w-10 text-purple-500 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-amber-700 font-medium">Dividend Yield</p>
                  <p className="text-2xl font-bold text-amber-600 mt-1">
                    {stockData.dividend_yield > 0 ? `${stockData.dividend_yield.toFixed(2)}%` : 'N/A'}
                  </p>
                </div>
                <DollarSign className="h-10 w-10 text-amber-500 opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="chart">Live Chart</TabsTrigger>
            <TabsTrigger value="valuation">Valuation</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <EnhancedStockChart
              symbol={stockData.ticker}
              height={450}
              onPriceUpdate={(data) => {
                setStockData(prev => ({
                  ...prev,
                  current_price: data.price,
                  price_change_today: data.change,
                  change_percent: data.changePercent,
                  volume: data.volume,
                }));
              }}
            />

            {stockData.description && (
              <Card>
                <CardHeader>
                  <CardTitle>About {stockData.company_name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed">
                    {stockData.description}
                  </p>
                  {stockData.website && (
                    <Button variant="outline" className="mt-4" asChild>
                      <a href={stockData.website} target="_blank" rel="noopener noreferrer">
                        <Globe className="h-4 w-4 mr-2" />
                        Visit Website
                      </a>
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="chart">
            <EnhancedStockChart
              symbol={stockData.ticker}
              height={600}
              onPriceUpdate={(data) => {
                setStockData(prev => ({
                  ...prev,
                  current_price: data.price,
                  price_change_today: data.change,
                  change_percent: data.changePercent,
                  volume: data.volume,
                }));
              }}
            />
          </TabsContent>

          <TabsContent value="valuation">
            <StockMetricsComparison
              stockData={stockData}
              valuationData={valuationData}
            />
          </TabsContent>

          <TabsContent value="details">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trading Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Day Range</span>
                      <span className="font-medium">
                        {formatCurrency(stockData.days_low)} - {formatCurrency(stockData.days_high)}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">52 Week Range</span>
                      <span className="font-medium">
                        {formatCurrency(stockData.fifty_two_week_low)} - {formatCurrency(stockData.fifty_two_week_high)}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Avg Volume (3M)</span>
                      <span className="font-medium">{formatVolume(stockData.avg_volume_3mon)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Beta</span>
                      <span className="font-medium">{stockData.beta ? stockData.beta.toFixed(2) : 'N/A'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Financial Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">EPS (TTM)</span>
                      <span className="font-medium">
                        {stockData.earnings_per_share ? formatCurrency(stockData.earnings_per_share) : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Forward P/E</span>
                      <span className="font-medium">
                        {stockData.forward_pe ? stockData.forward_pe.toFixed(2) : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Price/Book</span>
                      <span className="font-medium">
                        {stockData.price_to_book ? stockData.price_to_book.toFixed(2) : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Profit Margin</span>
                      <span className="font-medium">
                        {stockData.profit_margin ? `${stockData.profit_margin.toFixed(2)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Revenue Growth</span>
                      <span className="font-medium">
                        {stockData.revenue_growth ? `${stockData.revenue_growth.toFixed(2)}%` : 'N/A'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default EnhancedStockDetail;
