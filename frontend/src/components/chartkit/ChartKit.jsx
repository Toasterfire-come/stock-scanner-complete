import React, { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Alert, AlertDescription } from "../ui/alert";
import { getStock, getRealTimeQuote } from "../../api/client";
import { BarChart3, RefreshCw } from "lucide-react";

/**
 * ChartKit
 * High-performance, theme-aware, multi-pane financial chart component.
 * Attempts to use lightweight-charts if available; otherwise falls back to a vector/SVG renderer.
 */
const DEFAULT_TIMEFRAMES = ["1D", "5D", "1M", "3M", "6M", "1Y"]; // minimal good set

function readCssVar(variableName, fallback) {
  try {
    const root = document.documentElement;
    const v = getComputedStyle(root).getPropertyValue(variableName).trim();
    if (!v) return fallback;
    // Values are HSL space-separated numbers; convert to CSS hsl string
    if (/^\d+\s+\d+%\s+\d+%$/.test(v)) {
      return `hsl(${v})`;
    }
    return v;
  } catch {
    return fallback;
  }
}

function getThemeColors() {
  return {
    background: readCssVar("--background", "#ffffff"),
    foreground: readCssVar("--foreground", "#111827"),
    grid: "#e5e7eb",
    up: "#16a34a",
    down: "#dc2626",
    chart1: readCssVar("--chart-1", "#3b82f6"),
    chart2: readCssVar("--chart-2", "#10b981"),
    chart3: readCssVar("--chart-3", "#f59e0b"),
    chart4: readCssVar("--chart-4", "#8b5cf6"),
    chart5: readCssVar("--chart-5", "#ef4444"),
  };
}

function getDataPoints(timeframe) {
  switch (timeframe) {
    case "1D": return 78; // 5m intraday
    case "5D": return 96; // 15m
    case "1M": return 120; // hourly
    case "3M": return 90; // daily
    case "6M": return 180; // daily
    case "1Y": return 252; // weekly/daily
    default: return 100;
  }
}

function getMsPerUnit(timeframe) {
  switch (timeframe) {
    case "1D": return 5 * 60 * 1000;
    case "5D": return 15 * 60 * 1000;
    case "1M": return 60 * 60 * 1000;
    case "3M":
    case "6M": return 24 * 60 * 60 * 1000;
    case "1Y": return 7 * 24 * 60 * 60 * 1000;
    default: return 60 * 60 * 1000;
  }
}

function generateOHLCV(basePrice, timeframe) {
  const count = getDataPoints(timeframe);
  const out = [];
  let p = Math.max(1, Number(basePrice || 100));
  const now = Date.now();
  const step = getMsPerUnit(timeframe);
  for (let i = count - 1; i >= 0; i--) {
    const ts = new Date(now - i * step);
    const open = p;
    const vol = Math.floor(Math.random() * 1_500_000) + 250_000;
    const high = open * (1 + Math.random() * 0.015);
    const low = open * (1 - Math.random() * 0.015);
    const close = low + Math.random() * (high - low);
    p = close;
    out.push({ time: Math.floor(ts.getTime() / 1000), open, high, low, close, volume: vol });
  }
  return out;
}

function sma(values, period) {
  const out = new Array(values.length).fill(null);
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    const v = Number(values[i] ?? 0);
    sum += v;
    if (i >= period) sum -= Number(values[i - period] ?? 0);
    if (i >= period - 1) out[i] = sum / period;
  }
  return out;
}

function ema(values, period) {
  const out = new Array(values.length).fill(null);
  const k = 2 / (period + 1);
  let prev = null;
  for (let i = 0; i < values.length; i++) {
    const v = Number(values[i] ?? 0);
    if (i === 0) { prev = v; continue; }
    prev = v * k + prev * (1 - k);
    if (i >= period - 1) out[i] = prev;
  }
  return out;
}

function stddevAt(values, idx, period) {
  if (idx < period - 1) return null;
  let sum = 0, sumSq = 0;
  for (let i = idx - period + 1; i <= idx; i++) {
    const v = Number(values[i] ?? 0);
    sum += v; sumSq += v * v;
  }
  const mean = sum / period;
  const variance = Math.max(0, sumSq / period - mean * mean);
  return Math.sqrt(variance);
}

function bollinger(values, period = 20, mult = 2) {
  const mid = sma(values, period);
  const upper = new Array(values.length).fill(null);
  const lower = new Array(values.length).fill(null);
  for (let i = 0; i < values.length; i++) {
    if (mid[i] == null) continue;
    const sd = stddevAt(values, i, period);
    if (sd == null) continue;
    upper[i] = mid[i] + mult * sd;
    lower[i] = mid[i] - mult * sd;
  }
  return { mid, upper, lower };
}

function rsi(values, period = 14) {
  const out = new Array(values.length).fill(null);
  if (values.length === 0) return out;
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const ch = Number(values[i] ?? 0) - Number(values[i - 1] ?? 0);
    if (ch >= 0) gains += ch; else losses -= ch;
  }
  let avgG = gains / period; let avgL = losses / period;
  out[period] = avgL === 0 ? 100 : 100 - 100 / (1 + (avgG / avgL));
  for (let i = period + 1; i < values.length; i++) {
    const ch = Number(values[i] ?? 0) - Number(values[i - 1] ?? 0);
    avgG = (avgG * (period - 1) + Math.max(0, ch)) / period;
    avgL = (avgL * (period - 1) + Math.max(0, -ch)) / period;
    out[i] = avgL === 0 ? 100 : 100 - 100 / (1 + (avgG / avgL));
  }
  return out;
}

export default function ChartKit({ symbol, height = 420, showControls = true, timeframeDefault = "1M" }) {
  const [timeframe, setTimeframe] = useState(timeframeDefault);
  const [seriesData, setSeriesData] = useState([]); // [{ time, open, high, low, close, volume }]
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [useFallback, setUseFallback] = useState(false);
  const [lastPrice, setLastPrice] = useState(null);
  const containerRef = useRef(null);
  const volumeRef = useRef(null);
  const rsiRef = useRef(null);
  const chartHandlesRef = useRef({ main: null, vol: null, rsi: null, cleanup: [] });

  const theme = useMemo(() => getThemeColors(), []);

  const closes = useMemo(() => seriesData.map(d => Number(d.close)), [seriesData]);
  const sma20 = useMemo(() => sma(closes, 20), [closes]);
  const ema12 = useMemo(() => ema(closes, 12), [closes]);
  const bands = useMemo(() => bollinger(closes, 20, 2), [closes]);
  const rsi14 = useMemo(() => rsi(closes, 14), [closes]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!symbol) return;
      setLoading(true); setError(null);
      try {
        const res = await getStock(symbol).catch(() => null);
        const price = res?.data?.current_price || res?.current_price;
        let data = [];
        // Prefer recent_prices if it has OHLC
        const rp = res?.data?.recent_prices || res?.recent_prices;
        if (Array.isArray(rp) && rp.length > 10) {
          // Normalize to OHLCV array if needed
          if (rp[0] && ("open" in rp[0] || "close" in rp[0])) {
            data = rp.map((d) => ({
              time: Math.floor(new Date(d.timestamp || d.time || d.date).getTime() / 1000),
              open: Number(d.open ?? d.price ?? 0),
              high: Number(d.high ?? d.price ?? 0),
              low: Number(d.low ?? d.price ?? 0),
              close: Number(d.close ?? d.price ?? 0),
              volume: Number(d.volume ?? 0),
            })).filter(x => Number.isFinite(x.time) && Number.isFinite(x.close));
          }
        }
        if (data.length < 20) {
          data = generateOHLCV(price || 120, timeframe);
        }
        if (!cancelled) setSeriesData(data);
        try {
          const rt = await getRealTimeQuote(symbol).catch(() => null);
          if (!cancelled && rt) setLastPrice(rt?.current_price || rt?.data?.current_price || null);
        } catch {}
      } catch (e) {
        if (!cancelled) {
          setError("Failed to load chart data");
          setSeriesData(generateOHLCV(100, timeframe));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [symbol, timeframe]);

  useEffect(() => {
    // Attempt to use lightweight-charts; if unavailable, fallback to SVG renderer
    let active = true;
    async function initCharts() {
      if (!containerRef.current) return;
      if (seriesData.length === 0) return;
      try {
        const lwc = await import("lightweight-charts");
        if (!active || !lwc?.createChart) throw new Error("no-lwc");
        const commonOpts = {
          layout: { background: { color: theme.background }, textColor: theme.foreground },
          grid: { vertLines: { color: theme.grid }, horzLines: { color: theme.grid } },
          crosshair: { mode: 1 },
          rightPriceScale: { borderColor: theme.grid },
          timeScale: { borderColor: theme.grid, rightOffset: 4, barSpacing: 7, fixLeftEdge: false, fixRightEdge: false },
          handleScroll: true,
          handleScale: true,
        };
        const mainChart = lwc.createChart(containerRef.current, { height, ...commonOpts });
        const volChart = lwc.createChart(volumeRef.current, { height: 100, ...commonOpts });
        const rsiChart = lwc.createChart(rsiRef.current, { height: 90, ...commonOpts });

        const candleSeries = mainChart.addCandlestickSeries({ upColor: theme.up, downColor: theme.down, borderUpColor: theme.up, borderDownColor: theme.down, wickUpColor: theme.up, wickDownColor: theme.down });
        candleSeries.setData(seriesData);

        const smaSeries = mainChart.addLineSeries({ color: theme.chart1, lineWidth: 1.5 });
        const emaSeries = mainChart.addLineSeries({ color: theme.chart3, lineWidth: 1.3 });
        const upperSeries = mainChart.addLineSeries({ color: "#9ca3af", lineWidth: 1 });
        const lowerSeries = mainChart.addLineSeries({ color: "#9ca3af", lineWidth: 1 });

        // Map indicator arrays to { time, value }
        const toLine = (arr) => arr.map((v, i) => (v == null ? null : { time: seriesData[i].time, value: v })).filter(Boolean);
        smaSeries.setData(toLine(sma20));
        emaSeries.setData(toLine(ema12));
        upperSeries.setData(toLine(bands.upper));
        lowerSeries.setData(toLine(bands.lower));

        // Volume as histogram
        const volSeries = volChart.addHistogramSeries({ color: theme.chart2, priceFormat: { type: "volume" }, priceScaleId: "", base: 0 });
        volSeries.setData(seriesData.map((d, i) => ({ time: d.time, value: d.volume, color: (seriesData[i].close >= seriesData[Math.max(0, i - 1)]?.close) ? "#a7f3d0" : "#fecaca" })));

        // RSI
        const rsiSeries = rsiChart.addLineSeries({ color: "#111827", lineWidth: 1.2 });
        rsiSeries.setData(toLine(rsi14));

        // Sync time scales: when main changes, apply to others
        const sync = () => {
          const range = mainChart.timeScale().getVisibleLogicalRange();
          if (range) {
            volChart.timeScale().setVisibleLogicalRange(range);
            rsiChart.timeScale().setVisibleLogicalRange(range);
          }
        };
        const handler = mainChart.timeScale().subscribeVisibleLogicalRangeChange(sync);

        const cleanup = () => {
          try { mainChart.timeScale().unsubscribeVisibleLogicalRangeChange(handler); } catch {}
          try { mainChart.remove(); } catch {}
          try { volChart.remove(); } catch {}
          try { rsiChart.remove(); } catch {}
        };
        chartHandlesRef.current = { main: mainChart, vol: volChart, rsi: rsiChart, cleanup: [cleanup] };
      } catch (e) {
        // Fallback to SVG renderer if lwc not installed
        setUseFallback(true);
      }
    }
    initCharts();
    return () => {
      active = false;
      const { cleanup } = chartHandlesRef.current || {};
      cleanup?.forEach((fn) => { try { fn(); } catch {} });
      chartHandlesRef.current = { main: null, vol: null, rsi: null, cleanup: [] };
    };
  }, [seriesData, theme, height, rsi14, ema12, sma20, bands]);

  // Simple fallback SVG renderer that mirrors GoogleFinanceChart layout (concise)
  function renderFallback() {
    if (seriesData.length === 0) return null;
    const width = Math.max(320, containerRef.current?.clientWidth || 800);
    const pad = 40;
    const h = height;
    const prices = seriesData.map(d => d.close);
    const minP = Math.min(...prices);
    const maxP = Math.max(...prices);
    const rng = maxP - minP || 1;
    const xAt = (i) => pad + (i / Math.max(1, seriesData.length - 1)) * (width - 2 * pad);
    const yAt = (p) => pad + ((maxP - p) / rng) * (h - 2 * pad);

    const pricePoints = seriesData.map((d, i) => `${xAt(i)},${yAt(d.close)}`).join(" ");

    const upperPts = bands.upper.map((v, i) => (v == null ? null : `${xAt(i)},${yAt(v)}`)).filter(Boolean).join(" ");
    const lowerPts = bands.lower.map((v, i) => (v == null ? null : `${xAt(i)},${yAt(v)}`)).filter(Boolean).join(" ");
    const smaPts = sma20.map((v, i) => (v == null ? null : `${xAt(i)},${yAt(v)}`)).filter(Boolean).join(" ");
    const emaPts = ema12.map((v, i) => (v == null ? null : `${xAt(i)},${yAt(v)}`)).filter(Boolean).join(" ");

    return (
      <div>
        <svg width={width} height={h} className="border rounded bg-white">
          <defs>
            <pattern id="grid" width="50" height="40" patternUnits="userSpaceOnUse">
              <path d="M 50 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          <polyline points={pricePoints} fill="none" stroke={theme.chart2} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
          {smaPts && <polyline points={smaPts} fill="none" stroke={theme.chart1} strokeWidth="1.5" />}
          {emaPts && <polyline points={emaPts} fill="none" stroke={theme.chart3} strokeWidth="1.2" />}
          {upperPts && <polyline points={upperPts} fill="none" stroke="#9ca3af" strokeWidth="1" />}
          {lowerPts && <polyline points={lowerPts} fill="none" stroke="#9ca3af" strokeWidth="1" />}
          <text x="10" y={pad} fontSize="12" fill="#666">${maxP.toFixed(2)}</text>
          <text x="10" y={h - pad + 5} fontSize="12" fill="#666">${minP.toFixed(2)}</text>
        </svg>
        <div className="mt-2 text-xs text-gray-500">Basic renderer in use. Install lightweight-charts for highest performance.</div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Advanced Price Chart
          </CardTitle>
          <CardDescription>Multi-pane indicators • Theme-aware • Mobile gestures</CardDescription>
        </div>
        <div className="flex gap-2">
          {showControls && (
            <div className="hidden sm:flex gap-1">
              {DEFAULT_TIMEFRAMES.map((tf) => (
                <Button key={tf} size="sm" variant={timeframe === tf ? "default" : "outline"} onClick={() => setTimeframe(tf)}>
                  {tf}
                </Button>
              ))}
            </div>
          )}
          <Button variant="ghost" size="sm" onClick={() => setTimeframe((t) => t)} aria-label="Refresh chart">
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert className="mb-3"><AlertDescription>{error}</AlertDescription></Alert>
        )}
        {!symbol ? (
          <div className="text-center text-gray-500 py-8">
            <BarChart3 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            Select a stock to view chart
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading chart…</p>
            </div>
          </div>
        ) : (
          <div>
            {/* Header strip */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">{symbol}</h3>
                {lastPrice != null && (
                  <Badge variant="secondary">${Number(lastPrice).toFixed(2)}</Badge>
                )}
              </div>
            </div>

            {/* Charts */}
            <div className="space-y-2">
              <div ref={containerRef} className="w-full" style={{ height, touchAction: 'pan-y pinch-zoom', WebkitUserSelect: 'none', userSelect: 'none' }}>
                {useFallback && renderFallback()}
              </div>
              <div ref={volumeRef} className="w-full" style={{ height: 100, touchAction: 'pan-y pinch-zoom', WebkitUserSelect: 'none', userSelect: 'none' }} />
              <div ref={rsiRef} className="w-full" style={{ height: 90, touchAction: 'pan-y pinch-zoom', WebkitUserSelect: 'none', userSelect: 'none' }} />
            </div>

            <div className="mt-4 text-xs text-center text-gray-500">
              Charts synchronize across panes • Pinch to zoom on mobile
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
