import React, { useEffect, useRef, useMemo } from 'react';
import { createChart } from 'lightweight-charts';

function normalizeSeries(data) {
  // Accepts array of {timestamp|time, open, high, low, close, volume, price}
  // Returns candle series data when OHLC exists; else area series from price/close
  if (!Array.isArray(data)) return { candles: [], area: [] };
  const hasOhlc = data.some(d => d.open != null && d.high != null && d.low != null && d.close != null);
  if (hasOhlc) {
    const candles = data.map(d => ({
      time: toChartTime(d.timestamp ?? d.time),
      open: Number(d.open),
      high: Number(d.high),
      low: Number(d.low),
      close: Number(d.close),
    })).filter(v => Number.isFinite(v.open) && Number.isFinite(v.close));
    return { candles, area: [] };
  }
  const area = data.map(d => ({
    time: toChartTime(d.timestamp ?? d.time),
    value: Number(d.price ?? d.close),
  })).filter(v => Number.isFinite(v.value));
  return { candles: [], area };
}

function toChartTime(ts) {
  if (!ts) return undefined;
  if (typeof ts === 'number') return Math.floor(ts / 1000);
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return undefined;
  return Math.floor(d.getTime() / 1000);
}

export default function LightweightPriceChart({
  data,
  height = 420,
  theme = 'light',
  overlays = [], // optional array of overlay series: {name, values:[{time,value}], color}
  onReady,
  ariaLabel = 'Interactive price chart',
}) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const mainSeriesRef = useRef(null);
  const overlaySeriesRefs = useRef([]);

  const seriesData = useMemo(() => normalizeSeries(data || []), [data]);

  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const chart = createChart(el, {
      height,
      autoSize: true,
      layout: theme === 'dark' ? { background: { color: 'rgba(17,24,39,1)' }, textColor: '#e5e7eb' } : { background: { color: 'white' }, textColor: '#111827' },
      grid: {
        vertLines: { color: theme === 'dark' ? 'rgba(55,65,81,0.3)' : 'rgba(229,231,235,0.7)' },
        horzLines: { color: theme === 'dark' ? 'rgba(55,65,81,0.3)' : 'rgba(229,231,235,0.7)' },
      },
      rightPriceScale: { borderColor: theme === 'dark' ? '#374151' : '#e5e7eb' },
      timeScale: { borderColor: theme === 'dark' ? '#374151' : '#e5e7eb' },
      crosshair: { mode: 1 },
    });
    chartRef.current = chart;

    // Main series
    let mainSeries;
    if (seriesData.candles.length) {
      mainSeries = chart.addCandlestickSeries({ upColor: '#16a34a', downColor: '#dc2626', borderVisible: false, wickUpColor: '#16a34a', wickDownColor: '#dc2626' });
      mainSeries.setData(seriesData.candles);
    } else {
      mainSeries = chart.addAreaSeries({ lineColor: '#2563eb', topColor: 'rgba(37,99,235,0.25)', bottomColor: 'rgba(37,99,235,0.01)', lineWidth: 2 });
      mainSeries.setData(seriesData.area);
    }
    mainSeriesRef.current = mainSeries;

    // Overlays
    overlaySeriesRefs.current = (overlays || []).map(({ values, color = '#3b82f6', lineWidth = 1.5 }) => {
      const s = chart.addLineSeries({ color, lineWidth, priceLineVisible: false, lastValueVisible: false });
      if (Array.isArray(values)) s.setData(values.map(p => ({ time: toChartTime(p.time), value: Number(p.value) })).filter(v => Number.isFinite(v.value)));
      return s;
    });

    chart.timeScale().fitContent();
    if (typeof onReady === 'function') onReady({ chart, mainSeries });

    const ro = new ResizeObserver(() => { try { chart.applyOptions({}); } catch {} });
    ro.observe(el);
    return () => {
      try { ro.disconnect(); } catch {}
      try { overlaySeriesRefs.current.forEach(s => chart.removeSeries(s)); } catch {}
      try { chart.remove(); } catch {}
      chartRef.current = null;
      mainSeriesRef.current = null;
      overlaySeriesRefs.current = [];
    };
  }, [height, theme]);

  // Update main data when input changes
  useEffect(() => {
    const chart = chartRef.current; const series = mainSeriesRef.current;
    if (!chart || !series) return;
    if (series.setData && seriesData.candles.length) {
      if (series.priceScale && series.seriesType && series.seriesType() !== 'Candlestick') {
        // Recreate as candlestick if type changed
        try { chart.removeSeries(series); } catch {}
        const s = chart.addCandlestickSeries({ upColor: '#16a34a', downColor: '#dc2626', borderVisible: false, wickUpColor: '#16a34a', wickDownColor: '#dc2626' });
        s.setData(seriesData.candles);
        mainSeriesRef.current = s;
      } else {
        series.setData(seriesData.candles);
      }
    } else if (series.setData && seriesData.area.length) {
      if (series.priceScale && series.seriesType && series.seriesType() !== 'Area') {
        try { chart.removeSeries(series); } catch {}
        const s = chart.addAreaSeries({ lineColor: '#2563eb', topColor: 'rgba(37,99,235,0.25)', bottomColor: 'rgba(37,99,235,0.01)', lineWidth: 2 });
        s.setData(seriesData.area);
        mainSeriesRef.current = s;
      } else {
        series.setData(seriesData.area);
      }
    }
    chart.timeScale().fitContent();
  }, [seriesData]);

  // Update overlays on prop change
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    try { overlaySeriesRefs.current.forEach(s => chart.removeSeries(s)); } catch {}
    overlaySeriesRefs.current = (overlays || []).map(({ values, color = '#3b82f6', lineWidth = 1.5 }) => {
      const s = chart.addLineSeries({ color, lineWidth, priceLineVisible: false, lastValueVisible: false });
      if (Array.isArray(values)) s.setData(values.map(p => ({ time: toChartTime(p.time), value: Number(p.value) })).filter(v => Number.isFinite(v.value)));
      return s;
    });
  }, [overlays]);

  return (
    <div ref={containerRef} className="w-full" style={{ height }} role="img" aria-label={ariaLabel} />
  );
}
