const cache = new Map();

export function setCache(key, data, ttlMs = 30000) {
  cache.set(key, { data, ts: Date.now(), ttlMs });
}

export function getCache(key) {
  const item = cache.get(key);
  if (!item) return null;
  const fresh = Date.now() - item.ts < item.ttlMs;
  return fresh ? item.data : null;
}

export function clearCache(key) {
  if (key) cache.delete(key); else cache.clear();
}