/*
  Test script to verify the same endpoints used by the frontend pages:
  - Stocks list: GET /api/stocks/ (accumulate all pages; expect ~100 for this test)
  - Single stock: GET /api/stock/{symbol}/
  - News feed: GET /api/news/feed/
  - Symbol-specific news: GET /api/news/{symbol}/

  Usage:
    BACKEND_URL=https://api.retailtradescanner.com node scripts/test_api.js
  or
    REACT_APP_BACKEND_URL=https://api.retailtradescanner.com node scripts/test_api.js
*/

const axios = require('axios');

const BASE = (process.env.REACT_APP_BACKEND_URL || process.env.BACKEND_URL || '').replace(/\/$/, '');
if (!BASE) {
  console.error('REACT_APP_BACKEND_URL or BACKEND_URL must be set');
  process.exit(1);
}

const api = axios.create({
  baseURL: BASE + '/api',
  timeout: 20000,
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
});

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchAllStocks(params = {}) {
  const PAGE_SIZE = 500; // single page should cover ~100
  let offset = 0;
  const all = [];
  for (let page = 0; page < 10; page++) {
    const q = { ...params, limit: PAGE_SIZE, offset };
    const { data } = await api.get('/stocks/', { params: q });
    const items = Array.isArray(data) ? data : (data?.data || data?.results || []);
    if (!Array.isArray(items) || items.length === 0) break;
    all.push(...items);
    if (items.length < PAGE_SIZE) break;
    offset += PAGE_SIZE;
    // be nice
    await delay(100);
  }
  return all;
}

async function getStock(symbol) {
  const { data } = await api.get(`/stock/${encodeURIComponent(symbol)}/`);
  return data;
}

async function getNewsFeed(limit = 50) {
  try {
    const { data } = await api.get('/news/feed/', { params: { limit } });
    return data;
  } catch (err) {
    // Some environments require auth for /news/feed/ or may not expose it; fallback to WP
    if (err?.response && (err.response.status === 401 || err.response.status === 404)) {
      const { data } = await api.get('/wordpress/news/', { params: { limit } });
      return data;
    }
    throw err;
  }
}

async function getSymbolNews(symbol) {
  try {
    const { data } = await api.get(`/news/${encodeURIComponent(symbol)}/`);
    return data;
  } catch (err) {
    if (err?.response && (err.response.status === 401 || err.response.status === 404)) {
      // Fallback: request WP endpoint directly with ticker filter
      const { data } = await api.get('/wordpress/news/', { params: { limit: 50, ticker: symbol } });
      // Normalized return shape
      return { news: data?.data || [] };
    }
    throw err;
  }
}

(async () => {
  try {
    console.log('Backend:', BASE);

    // 1) Fetch all stocks
    const stocks = await fetchAllStocks();
    const countStocks = Array.isArray(stocks) ? stocks.length : 0;
    console.log('Stocks fetched:', countStocks);
    if (countStocks === 0) throw new Error('No stocks returned');

    // Pick a representative symbol: prefer AAPL if present else first
    let symbol = 'AAPL';
    if (!stocks.find(s => (s.ticker || s.symbol) === 'AAPL')) {
      const first = stocks[0];
      symbol = first?.ticker || first?.symbol || 'AAPL';
    }
    console.log('Sample symbol:', symbol);

    // 2) Fetch single stock detail
    const stockDetail = await getStock(symbol);
    const stockOk = !!(stockDetail && (stockDetail.success ? stockDetail.data : stockDetail));
    console.log('Single stock detail ok:', stockOk);

    // 3) Fetch general news feed
    const feed = await getNewsFeed(50);
    const newsItems = feed?.data?.news_items || feed?.data || feed?.news || [];
    console.log('News feed items:', Array.isArray(newsItems) ? newsItems.length : 0);

    // 4) Fetch symbol-specific news
    const symNews = await getSymbolNews(symbol);
    const symNewsItems = symNews?.news || symNews?.data || [];
    console.log(`News items for ${symbol}:`, Array.isArray(symNewsItems) ? symNewsItems.length : 0);

    console.log('DONE');
  } catch (err) {
    const status = err?.response?.status;
    console.error('ERROR', status || '', err?.message || err);
    process.exit(2);
  }
})();

