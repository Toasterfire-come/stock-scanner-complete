import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../../components/ui/dialog";
import { toast } from "sonner";
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  PieChart, 
  DollarSign,
  Trash2,
  Edit,
  Eye,
  BarChart3,
  Download,
  Calendar,
  Target,
  AlertCircle
} from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, AreaChart, Area } from 'recharts';
import { 
  getPortfolio, 
  addPortfolio, 
  deletePortfolio,
  exportPortfolioCSV,
  searchStocks,
  getStock,
  listStocks,
  getPlanLimits,
  listPortfolios,
  createPortfolio,
  createShareLinkForPortfolio
} from "../../api/client";

const Portfolio = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [isCreatePortfolioOpen, setIsCreatePortfolioOpen] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState("My Portfolio");
  const [analytics, setAnalytics] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newHolding, setNewHolding] = useState({
    symbol: "",
    shares: "",
    avg_cost: "",
    portfolio_name: "My Portfolio"
  });
  const [amountToInvest, setAmountToInvest] = useState("");
  const [currentPrice, setCurrentPrice] = useState(null);
  const [isFetchingPrice, setIsFetchingPrice] = useState(false);
  const [tickerSuggestions, setTickerSuggestions] = useState([]);
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [investInput, setInvestInput] = useState({});
  const [priceMap, setPriceMap] = useState({});

  useEffect(() => {
    fetchAllPortfolioData();
  }, []);

  // Autocomplete and price fetching
  useEffect(() => {
    const q = (newHolding.symbol || '').trim();
    if (!q) { setTickerSuggestions([]); return; }
    setIsSuggesting(true);
    const t = setTimeout(async () => {
      try {
        const res = await searchStocks(q).catch(() => null);
        const results = Array.isArray(res) ? res : (res?.results || res?.data || []);
        setTickerSuggestions((results || []).slice(0, 6));
      } finally {
        setIsSuggesting(false);
      }
    }, 200);
    return () => clearTimeout(t);
  }, [newHolding.symbol]);

  useEffect(() => {
    const sym = (newHolding.symbol || '').trim();
    if (!sym) { setCurrentPrice(null); return; }
    let mounted = true;
    (async () => {
      try {
        setIsFetchingPrice(true);
        const res = await getStock(sym).catch(() => null);
        const price = Number(res?.data?.current_price || res?.current_price || 0) || null;
        if (mounted) setCurrentPrice(price);
      } finally {
        if (mounted) setIsFetchingPrice(false);
      }
    })();
    return () => { mounted = false; };
  }, [newHolding.symbol]);

  useEffect(() => {
    const amt = Number(amountToInvest);
    if (!amt || !currentPrice || currentPrice <= 0) return;
    const shares = amt / currentPrice;
    setNewHolding((prev) => ({ ...prev, shares: shares.toFixed(6), avg_cost: currentPrice.toFixed(2) }));
  }, [amountToInvest, currentPrice]);

  const fetchAllPortfolioData = async () => {
    setIsLoading(true);
    try {
      // Fetch list of portfolios and current holdings (optionally filtered) in parallel
      const [
        listRes,
        portfolioResponse,
        allStocks
      ] = await Promise.all([
        listPortfolios().catch(() => ({ success: true, data: { portfolios: [], count: 0 } })),
        getPortfolio(selectedPortfolioId ? { portfolio_id: selectedPortfolioId } : {}).catch(() => ({ success: true, data: [], summary: { total_value: 0, total_gain_loss: 0, total_gain_loss_percent: 0, total_holdings: 0 } })),
        listStocks({}).catch(() => [])
      ]);

      const pList = Array.isArray(listRes?.data?.portfolios) ? listRes.data.portfolios : [];
      setPortfolios(pList);
      if (!selectedPortfolioId && pList.length > 0) {
        setSelectedPortfolioId(pList[0].id);
      }
      setPortfolio(portfolioResponse);
      setAnalytics(null);
      // Build a symbol -> current_price map from the stock list
      try {
        const map = {};
        const rows = Array.isArray(allStocks?.results) ? allStocks.results : (Array.isArray(allStocks) ? allStocks : []);
        for (const s of rows) {
          const sym = String(s?.symbol || s?.ticker || '').toUpperCase();
          const p = Number(s?.current_price);
          if (sym && Number.isFinite(p)) map[sym] = p;
        }
        setPriceMap(map);
      } catch { setPriceMap({}); }
    } catch (error) {
      console.error("Failed to load portfolio data:", error);
      toast.error("Failed to load portfolio data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddStock = async (e) => {
    e.preventDefault();
    
    if (!newHolding.symbol || !newHolding.shares || !newHolding.avg_cost) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Enforce plan limit for portfolios
    try {
      const limits = getPlanLimits();
      const currentCount = Array.isArray(holdings) ? holdings.length : 0;
      if (Number.isFinite(limits.portfolios) && limits.portfolios === 0 && currentCount >= 1) {
        toast.error("Your plan does not include portfolios");
        return;
      }
      if (Number.isFinite(limits.portfolios) && limits.portfolios > 0 && currentCount >= limits.portfolios) {
        toast.error("Portfolio limit reached for your plan");
        return;
      }
    } catch {}

    try {
      const response = await addPortfolio({
        symbol: newHolding.symbol.toUpperCase(),
        shares: parseFloat(newHolding.shares),
        avg_cost: parseFloat(newHolding.avg_cost),
        portfolio_name: newHolding.portfolio_name
      });

      if (response && response.success) {
        toast.success("Stock added to portfolio successfully");
        setIsAddModalOpen(false);
        setNewHolding({
          symbol: "",
          shares: "",
          avg_cost: "",
          portfolio_name: "My Portfolio"
        });
        // Refresh all portfolio data
        fetchAllPortfolioData();
      } else {
        throw new Error(response?.message || 'Failed to add stock');
      }
    } catch (error) {
      console.error("Failed to add stock:", error);
      toast.error(error.message || "Failed to add stock to portfolio");
    }
  };

  const handleCreatePortfolio = async (e) => {
    e.preventDefault();
    const name = (newPortfolioName || "").trim();
    if (!name) { toast.error("Enter a portfolio name"); return; }
    try {
      const res = await createPortfolio({ name });
      if (res?.success) {
        toast.success("Portfolio created");
        setIsCreatePortfolioOpen(false);
        setNewPortfolioName("My Portfolio");
        await fetchAllPortfolioData();
        if (res.data?.portfolio_id) setSelectedPortfolioId(res.data.portfolio_id);
      } else {
        toast.error(res?.error || "Failed to create portfolio");
      }
    } catch (err) {
      toast.error(err?.response?.data?.error || err?.message || "Failed to create portfolio");
    }
  };

  const handleDeleteStock = async (holdingId) => {
    if (!window.confirm("Are you sure you want to remove this stock from your portfolio?")) {
      return;
    }

    try {
      const response = await deletePortfolio(holdingId);
      if (response && response.success) {
        toast.success("Stock removed from portfolio");
        fetchAllPortfolioData();
      } else {
        throw new Error(response?.message || 'Failed to delete stock');
      }
    } catch (error) {
      console.error("Failed to delete stock:", error);
      toast.error(error.message || "Failed to remove stock from portfolio");
    }
  };

  const handleExportPortfolio = async () => {
    try {
      const csvData = await exportPortfolioCSV();
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("Portfolio exported successfully");
    } catch (error) {
      console.error("Failed to export portfolio:", error);
      // Fallback CSV from current state
      try {
        const rows = [["Symbol","Company","Shares","Avg Cost","Current Price","Current Value","Gain/Loss","Gain/Loss %"]];
        (portfolio?.data || []).forEach(h => {
          const shares = Number(h.shares || 0);
          const curPrice = Number((h.current_value && shares) ? (h.current_value / shares) : 0);
          const curVal = Number(h.current_value || (curPrice * shares));
          const cost = Number(h.avg_cost || 0);
          const gain = curVal - (shares * cost);
          const gainPct = shares * cost > 0 ? (gain / (shares * cost)) * 100 : 0;
          rows.push([
            h.symbol,
            String(h.name || '').replace(/,/g,' '),
            shares,
            cost.toFixed(2),
            curPrice.toFixed(2),
            curVal.toFixed(2),
            gain.toFixed(2),
            gainPct.toFixed(2)
          ]);
        });
        const content = rows.map(r => r.join(',')).join('\n');
        const blob2 = new Blob([content], { type: 'text/csv' });
        const url2 = window.URL.createObjectURL(blob2);
        const a2 = document.createElement('a');
        a2.style.display = 'none';
        a2.href = url2;
        a2.download = `portfolio_local_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a2);
        a2.click();
        window.URL.revokeObjectURL(url2);
        toast.success("Portfolio exported (local)");
      } catch (e2) {
        toast.error("Failed to export portfolio");
      }
    }
  };

  const toNumber = (v, d = 0) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : d;
  };

  const formatCurrency = (value) => {
    const n = toNumber(value, 0);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(n);
  };

  const formatPercent = (value) => {
    const n = toNumber(value, 0);
    const sign = n >= 0 ? '+' : '';
    return `${sign}${n.toFixed(2)}%`;
  };

  

  const portfolioSummaryRaw = analytics || portfolio?.summary || {
    total_value: 0,
    total_gain_loss: 0,
    total_gain_loss_percent: 0,
    day_change: 0,
    day_change_percent: 0
  };
  const portfolioSummary = {
    total_value: toNumber(portfolioSummaryRaw.total_value, 0),
    total_gain_loss: toNumber(portfolioSummaryRaw.total_gain_loss, 0),
    total_gain_loss_percent: toNumber(portfolioSummaryRaw.total_gain_loss_percent, 0),
    day_change: toNumber(portfolioSummaryRaw.day_change, 0),
    day_change_percent: toNumber(portfolioSummaryRaw.day_change_percent, 0),
  };

  const holdings = Array.isArray(portfolio?.data) ? portfolio.data : [];

  const getHoldingCalculations = (holding) => {
    const shares = toNumber(holding.shares, 0);
    const purchasePrice = toNumber(holding.avg_cost, 0);
    const sym = String(holding.symbol || holding.ticker || '').toUpperCase();
    const priceFromMap = toNumber(priceMap[sym], NaN);
    const fallbackCurrentValue = toNumber(holding.current_value, NaN);
    const currentPrice = Number.isFinite(priceFromMap)
      ? priceFromMap
      : (shares > 0 && Number.isFinite(fallbackCurrentValue) ? (fallbackCurrentValue / shares) : 0);
    const costBasis = shares * purchasePrice;
    const profit = (currentPrice - purchasePrice) * shares;
    const ratio = purchasePrice > 0 ? (currentPrice / purchasePrice) : 0;
    const percentChange = purchasePrice > 0 ? ((currentPrice - purchasePrice) / purchasePrice) * 100 : 0;
    return {
      shares,
      purchasePrice,
      currentPrice,
      currentValue: currentPrice * shares,
      costBasis,
      profit,
      ratio,
      percentChange,
    };
  };

  const totals = holdings.reduce((acc, h) => {
    const c = getHoldingCalculations(h);
    acc.currentValue += c.currentValue;
    acc.costBasis += c.costBasis;
    acc.profit += c.profit;
    return acc;
  }, { currentValue: 0, costBasis: 0, profit: 0 });
  const totalsPercent = totals.costBasis > 0 ? ((totals.currentValue - totals.costBasis) / totals.costBasis) * 100 : 0;

  // CSV time series handling (browser-side cached via localStorage)
  const VALUE_CSV_KEY = 'portfolio_value_timeseries_csv';
  const PROFIT_CSV_KEY = 'portfolio_profit_timeseries_csv';

  const parseCsv = (csvText) => {
    try {
      if (!csvText || typeof csvText !== 'string') return [];
      const rows = csvText.trim().split(/\r?\n/);
      if (rows.length <= 1) return [];
      const dataRows = rows.slice(1);
      return dataRows
        .map((r) => r.split(','))
        .filter((cols) => cols.length >= 2)
        .map((cols) => ({ ts: Number(cols[0]), value: Number(cols[1]) }))
        .filter((p) => Number.isFinite(p.ts) && Number.isFinite(p.value));
    } catch { return []; }
  };

  const toCsv = (rows) => {
    const header = 'timestamp,value';
    const body = (rows || []).map((r) => `${r.ts},${r.value}`).join('\n');
    return `${header}\n${body}`;
  };

  const loadSeries = (key) => parseCsv(localStorage.getItem(key) || '');
  const saveSeries = (key, rows) => localStorage.setItem(key, toCsv(rows));

  const upsertSnapshot = (key, value) => {
    const now = Date.now();
    const rows = loadSeries(key);
    const last = rows[rows.length - 1];
    // Update if last within 10 minutes, else append
    if (last && now - last.ts < 10 * 60 * 1000) {
      last.ts = now;
      last.value = value;
      saveSeries(key, rows);
    } else {
      const next = [...rows, { ts: now, value }];
      // Keep last 500 points max
      const trimmed = next.slice(-500);
      saveSeries(key, trimmed);
    }
  };

  // Update snapshots whenever totals recalc
  useEffect(() => {
    try {
      upsertSnapshot(VALUE_CSV_KEY, totals.currentValue);
      upsertSnapshot(PROFIT_CSV_KEY, totals.profit);
    } catch {}
  }, [totals.currentValue, totals.profit]);

  const valueSeries = loadSeries(VALUE_CSV_KEY);
  const profitSeries = loadSeries(PROFIT_CSV_KEY);
  const toChartData = (rows) => rows.map((r) => ({
    x: new Date(r.ts).toLocaleString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: '2-digit' }),
    y: r.value
  }));
  const valueChartData = toChartData(valueSeries);
  const profitChartData = toChartData(profitSeries);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-96" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-8 w-32 mb-2" />
                <Skeleton className="h-3 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
            <p className="text-gray-600">Track and analyze your investments</p>
          </div>
          {/* Portfolio selector */}
          <div className="ml-4">
            <label htmlFor="portfolio-select" className="sr-only">Select Portfolio</label>
            <select
              id="portfolio-select"
              className="border rounded-md px-2 py-2 text-sm"
              value={selectedPortfolioId || ''}
              onChange={(e) => setSelectedPortfolioId(e.target.value ? Number(e.target.value) : null)}
            >
              {portfolios.length === 0 && <option value="">No portfolios</option>}
              {portfolios.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <Button variant="outline" onClick={() => setIsCreatePortfolioOpen(true)}>New Portfolio</Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={async () => {
            try {
              if (!selectedPortfolioId) { toast.error('Select a portfolio'); return; }
              const res = await createShareLinkForPortfolio(selectedPortfolioId);
              if (res?.success && res?.url) {
                const link = `${window.location.origin}${res.url}`;
                await navigator.clipboard.writeText(link);
                toast.success('Share link copied');
              } else {
                toast.error('Failed to create share link');
              }
            } catch {
              toast.error('Failed to create share link');
            }
          }}>Share</Button>
          <Button onClick={handleExportPortfolio} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Stock
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Stock to Portfolio</DialogTitle>
                <DialogDescription>
                  Enter the stock details to add to your portfolio
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddStock} className="space-y-4">
                <div>
                  <Label htmlFor="symbol">Stock Symbol *</Label>
                  <Input
                    id="symbol"
                    value={newHolding.symbol}
                    onChange={(e) => setNewHolding({...newHolding, symbol: e.target.value.toUpperCase()})}
                    placeholder="AAPL"
                    required
                  />
                  {isSuggesting && <div className="text-xs text-gray-500 mt-1">Searching...</div>}
                  {tickerSuggestions.length > 0 && (
                    <div className="mt-2 border rounded-md bg-white max-h-48 overflow-auto">
                  {tickerSuggestions.map((s, idx) => (
                        <button
                          key={`${s.ticker || s.symbol}-${idx}`}
                          type="button"
                          className="w-full text-left px-3 py-2 hover:bg-gray-50"
                          onClick={() => {
                            const sym = String(s.ticker || s.symbol || '').toUpperCase();
                            setNewHolding({ ...newHolding, symbol: sym });
                            setTickerSuggestions([]);
                          }}
                        >
                          <span className="font-medium mr-2">{String(s.ticker || s.symbol || '').toUpperCase()}</span>
                          <span className="text-gray-600 text-sm">{String(s.company_name || s.name || '')}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <div>
                  <Label htmlFor="amount">Amount to Invest (optional)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={amountToInvest}
                    onChange={(e) => setAmountToInvest(e.target.value)}
                    placeholder="1000.00"
                  />
                  {currentPrice ? (
                    <div className="text-xs text-gray-600 mt-1">Current price ~ {formatCurrency(currentPrice)}{isFetchingPrice ? ' (updating...)' : ''}</div>
                  ) : (
                    <div className="text-xs text-gray-500 mt-1">Enter a valid symbol to load current price</div>
                  )}
                </div>
                <div>
                  <Label htmlFor="shares">Number of Shares *</Label>
                  <Input
                    id="shares"
                    type="number"
                    step="0.001"
                    value={newHolding.shares}
                    onChange={(e) => setNewHolding({...newHolding, shares: e.target.value})}
                    placeholder="100"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="avg_cost">Average Cost per Share *</Label>
                  <Input
                    id="avg_cost"
                    type="number"
                    step="0.01"
                    value={newHolding.avg_cost}
                    onChange={(e) => setNewHolding({...newHolding, avg_cost: e.target.value})}
                    placeholder="150.00"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="portfolio_name">Portfolio Name</Label>
                  <Input
                    id="portfolio_name"
                    value={newHolding.portfolio_name}
                    onChange={(e) => setNewHolding({...newHolding, portfolio_name: e.target.value})}
                    placeholder="My Portfolio"
                  />
                </div>
                <Button type="submit" className="w-full">
                  Add to Portfolio
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Create portfolio dialog */}
      <Dialog open={isCreatePortfolioOpen} onOpenChange={setIsCreatePortfolioOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Portfolio</DialogTitle>
            <DialogDescription>
              Name your new portfolio. Limits are enforced per your plan.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreatePortfolio} className="space-y-4">
            <div>
              <Label htmlFor="np-name">Portfolio Name</Label>
              <Input id="np-name" value={newPortfolioName} onChange={(e) => setNewPortfolioName(e.target.value)} placeholder="My Portfolio" />
            </div>
            <div className="flex gap-2">
              <Button type="submit" className="flex-1">Create</Button>
              <Button type="button" variant="outline" onClick={() => setIsCreatePortfolioOpen(false)}>Cancel</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-2xl font-bold">{formatCurrency(portfolioSummary.total_value)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className={`bg-gradient-to-r ${portfolioSummary.total_gain_loss >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Gain/Loss</p>
                <p className={`text-2xl font-bold ${portfolioSummary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(portfolioSummary.total_gain_loss)}
                </p>
                <p className={`text-sm ${portfolioSummary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(portfolioSummary.total_gain_loss_percent)}
                </p>
              </div>
              {portfolioSummary.total_gain_loss >= 0 ? 
                <TrendingUp className="h-8 w-8 text-green-600" /> : 
                <TrendingDown className="h-8 w-8 text-red-600" />
              }
            </div>
          </CardContent>
        </Card>

        <Card className={`bg-gradient-to-r ${portfolioSummary.day_change >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Today's Change</p>
                <p className={`text-2xl font-bold ${portfolioSummary.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(portfolioSummary.day_change || 0)}
                </p>
                <p className={`text-sm ${portfolioSummary.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(portfolioSummary.day_change_percent || 0)}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-50 to-purple-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Holdings</p>
                <p className="text-2xl font-bold">{holdings.length}</p>
                <p className="text-sm text-gray-600">Stocks tracked</p>
              </div>
              <PieChart className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        {/* Combined Totals */}
        <Card className="bg-gradient-to-r from-indigo-50 to-indigo-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Combined Totals</p>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Current Value</p>
                  <p className="text-lg font-semibold">{formatCurrency(totals.currentValue)}</p>
                  <p className="text-sm text-gray-600">Cost Basis</p>
                  <p className="text-lg font-semibold">{formatCurrency(totals.costBasis)}</p>
                  <p className={`text-sm ${totals.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>Profit</p>
                  <p className={`text-lg font-semibold ${totals.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>{formatCurrency(totals.profit)} ({formatPercent(totalsPercent)})</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Only (tabs removed) */}
          <Card>
            <CardHeader>
              <CardTitle>Your Holdings</CardTitle>
              <CardDescription>
                Manage your portfolio positions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {holdings.length === 0 ? (
                <div className="text-center py-12">
                  <PieChart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Holdings Yet</h3>
                  <p className="text-gray-600 mb-6">Start building your portfolio by adding your first stock position.</p>
                  <Button onClick={() => setIsAddModalOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Stock
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {holdings.map((holding, index) => {
                    const c = getHoldingCalculations(holding);
                    return (
                      <div key={index} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg">{holding.symbol}</h3>
                            <p className="text-sm text-gray-600">{holding.name || 'Company Name'}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">{c.shares} shares</p>
                            <p className="text-sm text-gray-600">@ {formatCurrency(c.currentPrice)}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                          <div className="text-sm">
                            <div className="text-gray-600">Current Value</div>
                            <div className="font-semibold">{formatCurrency(c.currentValue)}</div>
                          </div>
                          <div className="text-sm">
                            <div className="text-gray-600">Cost Basis</div>
                            <div className="font-semibold">{formatCurrency(c.costBasis)}</div>
                          </div>
                          <div className="text-sm">
                            <div className={`${c.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>Profit</div>
                            <div className={`font-semibold ${c.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>{formatCurrency(c.profit)} ({formatPercent(c.percentChange)})</div>
                          </div>
                        </div>
                        {/* Per-holding quick calculator */}
                        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div className="text-sm">
                            <label className="text-gray-600">Amount to Invest</label>
                            <Input
                              type="number"
                              className="mt-1"
                              placeholder="1000.00"
                              value={investInput[holding.symbol] || ''}
                              onChange={(e) => setInvestInput((prev) => ({ ...prev, [holding.symbol]: e.target.value }))}
                            />
                          </div>
                          <div className="text-sm flex items-end">
                            <div>
                              <div className="text-gray-600">Estimated Shares</div>
                              <div className="font-semibold">
                                {(() => {
                                  const amt = toNumber(investInput[holding.symbol], 0);
                                  return c.currentPrice > 0 && amt > 0 ? (amt / c.currentPrice).toFixed(6) : '—';
                                })()}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center justify-end mt-3">
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteStock(holding.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        {/* Performance Charts */}
        <div className="grid gap-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Total Value Over Time</CardTitle>
              <CardDescription>Browser-cached time series (no server required)</CardDescription>
            </CardHeader>
            <CardContent>
              {valueChartData.length ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={valueChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="valueFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563eb" stopOpacity={0.35}/>
                          <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="x" hide={false} tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={(v) => formatCurrency(v)} width={80} tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(v) => formatCurrency(v)} />
                      <Area type="monotone" dataKey="y" stroke="#2563eb" fillOpacity={1} fill="url(#valueFill)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-600">No data yet. This will populate as you view your portfolio.</div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Profit Over Time</CardTitle>
              <CardDescription>Browser-cached time series (no server required)</CardDescription>
            </CardHeader>
            <CardContent>
              {profitChartData.length ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={profitChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="x" hide={false} tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={(v) => formatCurrency(v)} width={80} tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(v) => formatCurrency(v)} />
                      <Line type="monotone" dataKey="y" stroke="#10b981" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-600">No data yet. This will populate as you view your portfolio.</div>
              )}
            </CardContent>
          </Card>
        </div>
      {/* End holdings only */}
    </div>
  );
};

export default Portfolio;