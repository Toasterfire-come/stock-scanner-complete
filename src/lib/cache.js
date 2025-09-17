// Simple cache implementation
const cache = new Map();

export function getCache(key) {
  const item = cache.get(key);
  if (!item) return null;
  
  const { data, expiry } = item;
  if (Date.now() > expiry) {
    cache.delete(key);
    return null;
  }
  
  return data;
}

export function setCache(key, data, ttlMs = 30000) {
  cache.set(key, {
    data,
    expiry: Date.now() + ttlMs
  });
}

export function clearCache() {
  cache.clear();
}