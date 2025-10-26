// Simple client for the indicator web worker
let worker;
let nextId = 1;
const pending = new Map();

function ensureWorker() {
  if (worker) return worker;
  try {
    // CRA + craco supports Worker(new URL(..., import.meta.url))
    worker = new Worker(new URL('../workers/indicatorWorker.js', import.meta.url));
  } catch {
    worker = new Worker('/workers/indicatorWorker.js');
  }
  worker.onmessage = (e) => {
    const { id, type, payload, error } = e.data || {};
    const entry = pending.get(id);
    if (!entry) return;
    pending.delete(id);
    if (type === 'result') entry.resolve(payload);
    else entry.reject(new Error(error || 'indicator worker error'));
  };
  worker.onerror = (err) => {
    for (const [, entry] of pending) entry.reject(err);
    pending.clear();
  };
  return worker;
}

export function computeIndicatorsInWorker(indicators, series) {
  const id = nextId++;
  const w = ensureWorker();
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    w.postMessage({ id, type: 'compute', payload: { indicators, series } });
  });
}
