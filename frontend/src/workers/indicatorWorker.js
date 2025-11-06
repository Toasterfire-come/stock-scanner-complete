// Lightweight indicator engine running in a Web Worker
// Expects messages: { id, type: 'compute', payload: { indicators, series } }
// series: { closes: number[], highs?: number[], lows?: number[], volumes?: number[] }

function sma(values, period) {
  const out = new Array(values.length).fill(null);
  if (period <= 1) return values.slice();
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    const v = Number(values[i]);
    sum += v;
    if (i >= period) sum -= Number(values[i - period]);
    if (i >= period - 1) out[i] = sum / period;
  }
  return out;
}

function ema(values, period) {
  const out = new Array(values.length).fill(null);
  const k = 2 / (period + 1);
  let prev = null;
  for (let i = 0; i < values.length; i++) {
    const v = Number(values[i]);
    if (i === 0) { prev = v; continue; }
    prev = v * k + prev * (1 - k);
    if (i >= period - 1) out[i] = prev;
  }
  return out;
}

function stddev(arr, idx, period) {
  if (idx < period - 1) return null;
  let sum = 0, sumSq = 0;
  for (let i = idx - period + 1; i <= idx; i++) {
    const v = Number(arr[i]);
    sum += v; sumSq += v * v;
  }
  const mean = sum / period;
  const variance = Math.max(0, (sumSq / period) - mean * mean);
  return Math.sqrt(variance);
}

function bollinger(values, period = 20, mult = 2) {
  const mid = sma(values, period);
  const upper = new Array(values.length).fill(null);
  const lower = new Array(values.length).fill(null);
  for (let i = 0; i < values.length; i++) {
    if (mid[i] == null) continue;
    const sd = stddev(values, i, period);
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
    const change = values[i] - values[i - 1];
    if (change >= 0) gains += change; else losses -= change;
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  out[period] = avgLoss === 0 ? 100 : 100 - 100 / (1 + (avgGain / avgLoss));
  for (let i = period + 1; i < values.length; i++) {
    const change = values[i] - values[i - 1];
    avgGain = (avgGain * (period - 1) + Math.max(0, change)) / period;
    avgLoss = (avgLoss * (period - 1) + Math.max(0, -change)) / period;
    out[i] = avgLoss === 0 ? 100 : 100 - 100 / (1 + (avgGain / avgLoss));
  }
  return out;
}

function macd(values, fast = 12, slow = 26, signal = 9) {
  const emaFast = ema(values, fast);
  const emaSlow = ema(values, slow);
  const macdArr = values.map((_, i) => (emaFast[i] != null && emaSlow[i] != null) ? (emaFast[i] - emaSlow[i]) : null);
  const signalLine = ema(macdArr.map(v => v == null ? 0 : v), signal);
  const hist = macdArr.map((v, i) => (v != null && signalLine[i] != null) ? (v - signalLine[i]) : null);
  return { macd: macdArr, signal: signalLine, hist };
}

function vwap(cl, hi, lo, vol) {
  const out = new Array(cl.length).fill(null);
  let cumPV = 0, cumV = 0;
  for (let i = 0; i < cl.length; i++) {
    const typical = ((Number(hi?.[i]) || 0) + (Number(lo?.[i]) || 0) + (Number(cl?.[i]) || 0)) / 3;
    const v = Number(vol?.[i]) || 0;
    cumPV += typical * v;
    cumV += v;
    out[i] = cumV > 0 ? cumPV / cumV : null;
  }
  return out;
}

function computeIndicators(indicators, series) {
  const { closes = [], highs = [], lows = [], volumes = [] } = series || {};
  const result = {};
  for (const ind of indicators || []) {
    const name = String(ind?.name || '').toLowerCase();
    try {
      if (name === 'sma') result[`sma${ind.period}`] = sma(closes, Number(ind.period || 20));
      else if (name === 'ema') result[`ema${ind.period}`] = ema(closes, Number(ind.period || 20));
      else if (name === 'bb' || name === 'bollinger') result[`bb${ind.period || 20}`] = bollinger(closes, Number(ind.period || 20), Number(ind.mult || 2));
      else if (name === 'rsi') result[`rsi${ind.period || 14}`] = rsi(closes, Number(ind.period || 14));
      else if (name === 'macd') result['macd'] = macd(closes, Number(ind.fast || 12), Number(ind.slow || 26), Number(ind.signal || 9));
      else if (name === 'vwap') result['vwap'] = vwap(closes, highs, lows, volumes);
    } catch (e) {
      result[name] = null;
    }
  }
  return result;
}

self.onmessage = function(e) {
  const msg = e?.data || {};
  if (msg.type === 'compute') {
    const t0 = performance.now();
    try {
      const output = computeIndicators(msg.payload?.indicators, msg.payload?.series);
      const ms = performance.now() - t0;
      self.postMessage({ id: msg.id, type: 'result', payload: { output, ms } });
    } catch (err) {
      self.postMessage({ id: msg.id, type: 'error', error: String(err) });
    }
  }
};
