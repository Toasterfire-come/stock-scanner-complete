(function(){
  const base = (window.finmConfig && window.finmConfig.restBase) ? window.finmConfig.restBase.replace(/\/$/, '') : '/wp-json/finm/v1';
  function getCid(){
    try{
      const m = document.cookie.match(/(?:^|; )finm_cid=([^;]+)/); if(m) return decodeURIComponent(m[1]);
    }catch(e){}
    try{ const s = localStorage.getItem('finm_cid'); if(s) return s; }catch(e){}
    const gen = (Math.random().toString(36).slice(2)+Date.now().toString(36));
    try{ localStorage.setItem('finm_cid', gen); }catch(e){}
    return gen;
  }
  async function http(method, p, params, body){
    let url = base + p;
    if (params) url += '?' + new URLSearchParams(params);
    const r = await fetch(url, {
      method,
      headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: body ? JSON.stringify(body) : undefined
    });
    if(r.status === 401){
      try { window.dispatchEvent(new CustomEvent('finm:unauthorized')); }catch(e){}
      throw new Error('HTTP 401');
    }
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }
  const GET = (p, params) => http('GET', p, params);
  const POST = (p, body) => http('POST', p, undefined, body);
  const DEL = (p) => http('DELETE', p);

  const finmApi = {
    // Health & docs
    health: () => GET('/health'),
    docs: () => GET('/docs'),

    // Market data
    stocks: (params) => GET('/stocks', params),
    stock: (ticker) => GET('/stock/' + encodeURIComponent(ticker)),
    search: (q) => GET('/search', { q }),
    trending: () => GET('/trending'),
    marketStats: () => GET('/market-stats'),
    endpointStatus: () => GET('/endpoint-status'),

    // Revenue
    revenueAnalytics: (month) => month ? GET('/revenue/analytics/' + encodeURIComponent(month)) : GET('/revenue/analytics'),
    revenueValidate: (code) => POST('/revenue/validate-discount/', { code }),
    revenueApply: (code, amount) => POST('/revenue/apply-discount/', { code, amount }),
    revenueRecord: (payload) => POST('/revenue/record-payment/', payload),

    // WordPress helpers on the backend
    wpStocks: (params) => GET('/api/wordpress/stocks/', params),
    wpNews: (params) => GET('/api/wordpress/news/', params),
    wpAlerts: (params) => GET('/api/wordpress/alerts/', params),

    // Generic API passthroughs
    apiGet: (path, params) => GET('/api/' + String(path).replace(/^\//,''), params),
    apiPost: (path, payload) => POST('/api/' + String(path).replace(/^\//,''), payload),
    apiDelete: (path) => DEL('/api/' + String(path).replace(/^\//,'')),
    revenueGet: (path, params) => GET('/revenue/' + String(path).replace(/^\//,''), params),
    revenuePost: (path, payload) => POST('/revenue/' + String(path).replace(/^\//,''), payload),

    // Common endpoints from the spec
    realtime: (ticker) => finmApi.apiGet('realtime/' + encodeURIComponent(ticker) + '/'),
    filter: (params) => finmApi.apiGet('filter/', params),
    statistics: () => finmApi.apiGet('statistics/'),
    alertsCreateInfo: () => finmApi.apiGet('alerts/create/'),
    alertsCreate: (payload) => finmApi.apiPost('alerts/create/', payload),
    subscription: (payload) => finmApi.apiPost('subscription/', payload),
    subscribeWordPress: (payload) => finmApi.apiPost('wordpress/subscribe/', payload),

    // Auth + user (server sets cookies)
    authLogin: (username, password) => finmApi.apiPost('auth/login/', { username, password }),
    authLogout: () => finmApi.apiPost('auth/logout/', {}),
    userProfileGet: () => finmApi.apiGet('user/profile/'),
    userProfileUpdate: (data) => finmApi.apiPost('user/profile/', data),
    userChangePassword: (current_password, new_password, confirm_password) => finmApi.apiPost('user/change-password/', { current_password, new_password, confirm_password }),

    // Billing
    billingHistory: (page=1, limit=20) => finmApi.apiGet('user/billing-history/', { page, limit }),
    billingCurrentPlan: () => finmApi.apiGet('billing/current-plan/'),
    billingChangePlan: (plan_type, billing_cycle) => finmApi.apiPost('billing/change-plan/', { plan_type, billing_cycle }),
    billingStats: () => finmApi.apiGet('billing/stats/'),

    // Notifications
    notificationsHistory: (params) => finmApi.apiGet('notifications/history/', params),
    notificationsMarkRead: (notification_ids, mark_all=false) => finmApi.apiPost('notifications/mark-read/', { notification_ids, mark_all }),
    notificationsSettingsGet: () => finmApi.apiGet('notifications/settings/'),
    notificationsSettingsUpdate: (payload) => finmApi.apiPost('notifications/settings/', payload),

    // Portfolio
    portfolioGet: () => finmApi.apiGet('portfolio/'),
    portfolioAdd: (symbol, shares, avg_cost, portfolio_name) => finmApi.apiPost('portfolio/add/', { symbol, shares, avg_cost, portfolio_name }),
    portfolioDelete: (holding_id) => finmApi.apiDelete('portfolio/' + encodeURIComponent(holding_id) + '/'),

    // Watchlist
    watchlistGet: () => finmApi.apiGet('watchlist/'),
    watchlistAdd: (symbol, watchlist_name, notes, alert_price) => finmApi.apiPost('watchlist/add/', { symbol, watchlist_name, notes, alert_price }),
    watchlistDelete: (item_id) => finmApi.apiDelete('watchlist/' + encodeURIComponent(item_id) + '/'),

    // Usage tracking
    usageTrack: (action, ticker) => finmApi.apiPost('usage/track/', { client_id: getCid(), action, ticker, timestamp: new Date().toISOString() })
  };
  window.finmApi = finmApi;

  // Progressive enhancement: hydrate mock stocks/news from external API if configured
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
      }
    } catch(e){ console.warn('FinMarkets API stocks not available', e); }

    try {
      let news = [];
      try { news = await finmApi.wpNews({ limit: 12 }); } catch(_) {}
      if (!Array.isArray(news) || !news.length) {
        try { const n2 = await finmApi.apiGet('news/', { limit: 12 }); news = Array.isArray(n2) ? n2 : (n2?.data || []); } catch(_) {}
      }
      const mappedNews = (news||[]).map(n => ({
        title: n.title || n.headline || n.name || '—',
        source: n.source || n.publisher || '—',
        time: n.published_at || n.time || ''
      }));
      if(mappedNews.length){
        window.MockData = window.MockData || { stocks: [] };
        window.MockData.news = mappedNews;
      }
    } catch(e){ console.warn('FinMarkets API news not available', e); }

    document.dispatchEvent(new CustomEvent('finm:api-ready'));
  }
  document.addEventListener('DOMContentLoaded', enhanceMock);
})();