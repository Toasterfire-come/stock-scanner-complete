(function(){
  const base = (window.finmConfig && window.finmConfig.restBase) ? window.finmConfig.restBase.replace(/\/$/, '') : '/wp-json/finm/v1';
  const GET = async (p, params) => {
    const url = base + p + (params ? ('?' + new URLSearchParams(params)) : '');
    const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  };
  const finmApi = {
    health: () => GET('/health'),
    stocks: (params) => GET('/stocks', params),
    stock: (ticker) => GET('/stock/' + encodeURIComponent(ticker)),
    search: (q) => GET('/search', { q }),
    trending: () => GET('/trending'),
    marketStats: () => GET('/market-stats'),
    endpointStatus: () => GET('/endpoint-status'),
    revenueAnalytics: (month) => month ? GET('/revenue/analytics/' + encodeURIComponent(month)) : GET('/revenue/analytics')
  };
  window.finmApi = finmApi;

  // Progressive enhancement: if external API configured, try to hydrate mock data
  async function enhanceMock(){
    if(!(window.finmConfig && window.finmConfig.hasApiBase)) return;
    try {
      const h = await finmApi.health();
      const st = await finmApi.stocks({ limit: 25, sort_by: 'market_cap', sort_order: 'desc' });
      if(st && (st.data || Array.isArray(st))){
        const arr = Array.isArray(st) ? st : (st.data || []);
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
      }
      console.log('FinMarkets API health:', h);
    } catch(e){ console.warn('FinMarkets API not available', e); }
  }
  document.addEventListener('DOMContentLoaded', enhanceMock);
})();