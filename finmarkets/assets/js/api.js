(function(){
  const base = (window.finmConfig && window.finmConfig.restBase) ? window.finmConfig.restBase.replace(/\/$/, '') : '/wp-json/finm/v1';
  async function http(method, p, params, body){
    let url = base + p;
    if (params) url += '?' + new URLSearchParams(params);
    const r = await fetch(url, {
      method,
      headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }
  const GET = (p, params) => http('GET', p, params);
  const POST = (p, body) => http('POST', p, undefined, body);

  const finmApi = {
    // Specific helpers
    health: () => GET('/health'),
    stocks: (params) => GET('/stocks', params),
    stock: (ticker) => GET('/stock/' + encodeURIComponent(ticker)),
    search: (q) => GET('/search', { q }),
    trending: () => GET('/trending'),
    marketStats: () => GET('/market-stats'),
    endpointStatus: () => GET('/endpoint-status'),
    revenueAnalytics: (month) => month ? GET('/revenue/analytics/' + encodeURIComponent(month)) : GET('/revenue/analytics'),

    // Generic proxies aligned with the spec
    apiGet: (path, params) => GET('/api/' + String(path).replace(/^\//,''), params),
    apiPost: (path, payload) => POST('/api/' + String(path).replace(/^\//,''), payload),
    revenueGet: (path, params) => GET('/revenue/' + String(path).replace(/^\//,''), params),
    revenuePost: (path, payload) => POST('/revenue/' + String(path).replace(/^\//,''), payload),

    // Common endpoints from the spec
    realtime: (ticker) => finmApi.apiGet('realtime/' + encodeURIComponent(ticker) + '/'),
    filter: (params) => finmApi.apiGet('filter/', params),
    statistics: () => finmApi.apiGet('statistics/'),
    alertsCreateInfo: () => finmApi.apiGet('alerts/create/'),
    alertsCreate: (payload) => finmApi.apiPost('alerts/create/', payload),
    subscription: (payload) => finmApi.apiPost('subscription/', payload),
    wpStocks: (params) => finmApi.apiGet('wordpress/stocks/', params),
    wpNews: (params) => finmApi.apiGet('wordpress/news/', params),
    wpAlerts: (params) => finmApi.apiGet('wordpress/alerts/', params),
    revenueValidate: (code) => finmApi.revenuePost('validate-discount/', { code }),
    revenueApply: (code, amount) => finmApi.revenuePost('apply-discount/', { code, amount }),
  };
  window.finmApi = finmApi;

  // Progressive enhancement: hydrate mock stocks from external API if configured
  async function enhanceMock(){
    if(!(window.finmConfig && window.finmConfig.hasApiBase)) return;
    try {
      const st = await finmApi.stocks({ limit: 50, sort_by: 'market_cap', sort_order: 'desc' });
      const arr = Array.isArray(st) ? st : (st?.data || []);
      const mapped = arr.map(x => ({
        symbol: x.ticker || x.symbol,
        name: x.company_name || x.name || '—',
        sector: x.sector || '—',
        price: x.current_price || x.price || 0,
        change: (x.change_percent != null ? x.change_percent : (x.price_change_today || 0)),
        marketCap: x.market_cap || x.market_capitalization || 0
      })).filter(r => r.symbol);
      if(mapped.length) {
        window.MockData = window.MockData || { news: [] };
        window.MockData.stocks = mapped;
        document.dispatchEvent(new CustomEvent('finm:api-ready'));
      }
    } catch(e){ console.warn('FinMarkets API not available', e); }
  }
  document.addEventListener('DOMContentLoaded', enhanceMock);
})();