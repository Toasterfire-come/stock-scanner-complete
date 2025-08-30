(function(window, document){
  'use strict';
  
  // Configuration and performance optimization
  const cfg = window.rtsConfig || {};
  const apiBase = (cfg.apiBase || '').replace(/\/?$/, '/');
  const revenueBase = (cfg.revenueBase || '').replace(/\/?$/, '/');
  const isDebug = cfg.isDebug || false;
  
  // Performance: Use requestIdleCallback for non-critical operations
  const scheduleWork = window.requestIdleCallback || ((fn) => setTimeout(fn, 1));
  
  // Optimized DOM utilities with caching
  const domCache = new Map();
  const $ = (sel, root=document) => {
    const key = `${sel}:${root === document ? 'doc' : 'other'}`;
    if (!domCache.has(key)) {
      domCache.set(key, root.querySelector(sel));
    }
    return domCache.get(key);
  };
  
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));
  
  // Optimized debounce with immediate option
  const debounce = (fn, wait=250, immediate=false) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        if (!immediate) fn.apply(this, args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) fn.apply(this, args);
    };
  };
  
  // Performance: Throttle for high-frequency events
  const throttle = (fn, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        fn.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  };
  
  // Utility functions with performance improvements
  const clamp = (num, min, max) => Math.min(Math.max(num, min), max);
  const fmtInt = (n) => (typeof n === 'number') ? n.toLocaleString() : (n||'');
  const fmtMoney = (n) => (typeof n === 'number') ? n.toLocaleString(undefined, { maximumFractionDigits: 2 }) : (n||'');
  
  // Performance: Batch DOM updates
  const batchDOMUpdates = (updates) => {
    requestAnimationFrame(() => {
      updates.forEach(update => update());
    });
  };
  
  // API origin derivation with caching
  let _apiOrigin = null;
  function apiOrigin(){ 
    if (_apiOrigin === null) {
      try { 
        _apiOrigin = apiBase ? new URL(apiBase).origin : ''; 
      } catch(e){ 
        _apiOrigin = ''; 
      }
    }
    return _apiOrigin;
  }

  // Toasts
  function ensureToastRoot(){ let r = $('#rts-toasts'); if (!r){ r = document.createElement('div'); r.id = 'rts-toasts'; document.body.appendChild(r); } return r; }
  function showToast(msg, type='info'){ const root = ensureToastRoot(); const div = document.createElement('div'); div.className = 'toast ' + (type==='error'?'toast-error':type==='success'?'toast-success':''); div.textContent = msg; root.appendChild(div); setTimeout(()=>{ div.classList.add('out'); setTimeout(()=>div.remove(), 300); }, 2500); }

  // Skeleton helper
  function setSkeleton(node, active){ if(!node) return; node.classList.toggle('skeleton', !!active); }

  // API wrapper
  const API = {
    base: apiBase,
    revBase: revenueBase,
    build(base, path){ if (!base) return ''; const p = (path||'').replace(/^\//,''); return base + p; },
    async req(method, path, { params, body }={}){
      if (!apiBase){ console.warn('API base missing; skipping request', path); return null; }
      const url = new URL(this.build(apiBase, path));
      if (params){ Object.entries(params).forEach(([k,v]) => (v!==''&&v!=null) && url.searchParams.set(k, v)); }
      try{
        const res = await fetch(url.toString(), {
          method,
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: body ? JSON.stringify(body) : undefined,
        });
        if (!res.ok) throw new Error('HTTP '+res.status);
        const ct = res.headers.get('content-type')||'';
        return ct.includes('application/json') ? await res.json() : await res.text();
      }catch(e){ console.warn('API error', method, url.toString(), e); showToast('Network error loading data', 'error'); return null; }
    },
    get(path, params){ return this.req('GET', path, { params }); },
    post(path, body){ return this.req('POST', path, { body }); },
    del(path){ return this.req('DELETE', path); }
  };

  function notifyMissingApi(){ if (apiBase) return; $$('#rts-kpis, #rts-trending-gainers, #rts-trending-active, #rts-scanner-results, #rts-watchlist, #rts-portfolio, #rts-alerts-list, #rts-news, #rts-api-docs, #rts-endpoint-status').forEach(el => { if (el) el.textContent = 'API not configured. Please set API URL.'; }); }

  // Health indicator (header)
  async function initHealthIndicator(){ const dot = $('#rts-health-dot'); if(!dot || !apiBase) return; const data = await API.get('health/'); let color = '#f59e0b'; if (data && (data.status==='healthy' || data.success===true)) color='#10b981'; if (!data) color='#ef4444'; dot.style.backgroundColor=color; dot.title = data ? ('API: '+(data.status||'ok')) : 'API: unreachable'; }

  // Dashboard
  async function initDashboard(){ const kpis = $('#rts-kpis'); const gainers = $('#rts-trending-gainers'); const active = $('#rts-trending-active'); if(!kpis && !gainers && !active) return; setSkeleton(kpis, true); const stats = await API.get('market-stats/'); setSkeleton(kpis, false); if (kpis){ if (stats && stats.market_overview){ const mo = stats.market_overview; kpis.innerHTML = ''+
      '<div class="card p-3"><div>Total Stocks</div><div class="text-lg">'+(mo.total_stocks??'-')+'</div></div>'+
      '<div class="card p-3"><div>Gainers</div><div class="text-lg">'+(mo.gainers??'-')+'</div></div>'+
      '<div class="card p-3"><div>Losers</div><div class="text-lg">'+(mo.losers??'-')+'</div></div>'+
      '<div class="card p-3"><div>Unchanged</div><div class="text-lg">'+(mo.unchanged??'-')+'</div></div>'; } else { kpis.textContent='No market data'; } }
    const trend = await API.get('trending/'); const renderList=(el,arr)=>{ if(!el) return; if(!arr||!arr.length){ el.textContent='No data'; return; } el.innerHTML = arr.slice(0,10).map(x=>'<div class="border rounded p-2 flex justify-between"><span>'+(x.ticker||x.name)+'</span><span>'+(x.current_price??'-')+'<span class="text-xs text-muted-foreground ml-2">'+(x.change_percent!=null? (x.change_percent.toFixed? x.change_percent.toFixed(2):x.change_percent)+'%':'' )+'</span></span></div>').join(''); };
    if (trend){ renderList(gainers, trend.top_gainers||trend.high_volume); renderList(active, trend.most_active); }
  }

  // Scanner
  function initScanner(){ const form = $('#rts-scanner-form'); const results = $('#rts-scanner-results'); const ac = $('#rts-search'); if(!form || !results) return; async function runSearch(params){ setSkeleton(results,true); const preferFilter = params && (params.sector || params.order_by || params.offset!=null); const endpoint = preferFilter ? 'filter/' : 'stocks/'; const data = await API.get(endpoint, params); setSkeleton(results,false); if(!data || data.success===false){ results.textContent='No results'; return; } const list=(data.data||data.stocks||[]); const rows=list.slice(0,100).map(r=>'<tr class="border-t">\n<td class="px-3 py-2">'+(r.ticker||r.symbol)+'</td>\n<td class="px-3 py-2">'+(r.company_name||r.name||'')+'</td>\n<td class="px-3 py-2">'+fmtMoney(r.current_price)+'</td>\n<td class="px-3 py-2">'+(r.change_percent!=null? (r.change_percent.toFixed? r.change_percent.toFixed(2):r.change_percent)+'%':'')+'</td>\n<td class="px-3 py-2">'+fmtInt(r.volume)+'</td>\n<td class="px-3 py-2">'+fmtInt(r.market_cap)+'</td>\n<td class="px-3 py-2">'+(r.last_updated||'')+'</td>\n</tr>').join(''); const meta = (data.total_available!=null||data.count!=null) ? '<div class="text-xs text-muted-foreground mt-2">'+(data.count!=null?('Count: '+fmtInt(data.count)+' '):'')+(data.total_available!=null?('Total: '+fmtInt(data.total_available)+' '):'')+'</div>' : ''; results.innerHTML = '<div class="overflow-x-auto rounded-lg border">\n<table class="min-w-full text-sm"><thead class="bg-muted/50 text-muted-foreground"><tr><th class="px-3 py-2 text-left">Ticker</th><th class="px-3 py-2 text-left">Name</th><th class="px-3 py-2 text-left">Price</th><th class="px-3 py-2 text-left">Change %</th><th class="px-3 py-2 text-left">Volume</th><th class="px-3 py-2 text-left">Market Cap</th><th class="px-3 py-2 text-left">Updated</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+meta; }
    form.addEventListener('submit', function(e){ e.preventDefault(); const fd=new FormData(form); const params=Object.fromEntries(fd.entries()); if (params.limit){ const n=Number(params.limit); if (!Number.isNaN(n)) params.limit = String(clamp(n, 1, 1000)); else delete params.limit; } runSearch(params); }); if (ac){ ac.addEventListener('input', debounce(async ()=>{ const v=ac.value.trim(); if(!v) return; const data = await API.get('search/', { q: v }); const sug = $('#rts-autocomplete'); if (!sug) return; sug.innerHTML = (data&&data.results?data.results.slice(0,8):[]).map(r=>'<div class="px-2 py-1 hover:underline">'+(r.ticker||r.company_name)+'</div>').join(''); }, 250)); }
  }

  // Watchlists
  function initWatchlists(){ const list=$('#rts-watchlist'); const addForm=$('#rts-watchlist-add'); async function load(){ if(!list) return; setSkeleton(list,true); const data=await API.get('watchlist/'); setSkeleton(list,false); if(!data||data.success===false){ list.textContent='No items'; return; } list.innerHTML=(data.data||[]).map(i=>'<div class="border rounded p-2 flex justify-between"><span>'+i.symbol+' • '+(i.company_name||'')+' • '+fmtMoney(i.current_price)+'</span><button data-id="'+i.id+'" class="rts-wl-del border rounded px-2">Remove</button></div>').join(''); }
    document.addEventListener('click', async (e)=>{ const btn=e.target.closest('.rts-wl-del'); if(!btn) return; e.preventDefault(); const id=btn.getAttribute('data-id'); const res=await API.del('watchlist/'+id+'/'); if(!res){ showToast('Failed to remove','error'); } await load(); }); if(addForm){ addForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(addForm); const body=Object.fromEntries(fd.entries()); const res=await API.post('watchlist/add/', body); const ok = !!(res && res.success!==false); showToast(ok ? 'Added to watchlist' : 'Failed to add', ok ? 'success' : 'error'); if (ok) { addForm.reset(); } await load(); }); }
    load(); }

  // Portfolio
  function initPortfolio(){ const list=$('#rts-portfolio'); const addForm=$('#rts-portfolio-add'); if (list && !list.innerHTML.trim()) { list.innerHTML = '<div class="text-muted-foreground">No holdings</div>'; } async function load(){ if(!list) return; setSkeleton(list,true); const data=await API.get('portfolio/'); setSkeleton(list,false); if(!data||data.success===false||!(data.data||[]).length){ list.innerHTML='<div class="text-muted-foreground">No holdings</div>'; return; } const rows=(data.data||[]).map(h=>'<tr class="border-t"><td class="px-3 py-2">'+h.symbol+'</td><td class="px-3 py-2">'+fmtMoney(h.shares)+'</td><td class="px-3 py-2">'+fmtMoney(h.avg_cost)+'</td><td class="px-3 py-2">'+(h.current_price!=null? fmtMoney(h.current_price):'')+'</td><td class="px-3 py-2"><button data-id="'+h.id+'" class="rts-port-del border rounded px-2">Remove</button></td></tr>').join(''); list.innerHTML='<div class="overflow-x-auto rounded-lg border">\n<table class="min-w-full text-sm"><thead class="bg-muted/50 text-muted-foreground"><tr><th class="px-3 py-2 text-left">Symbol</th><th class="px-3 py-2 text-left">Shares</th><th class="px-3 py-2 text-left">Avg Cost</th><th class="px-3 py-2 text-left">Price</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>'; }
    document.addEventListener('click', async (e)=>{ const btn=e.target.closest('.rts-port-del'); if(!btn) return; e.preventDefault(); const id=btn.getAttribute('data-id'); const res=await API.del('portfolio/'+id+'/'); if(!res){ showToast('Failed to remove holding','error'); } await load(); }); if(addForm){ addForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(addForm); const body=Object.fromEntries(fd.entries()); const res=await API.post('portfolio/add/', body); const ok = !!(res && res.success!==false); showToast(ok ? 'Holding added' : 'Failed to add holding', ok ? 'success' : 'error'); if (ok) { addForm.reset(); } await load(); }); }
    load(); }

  // Alerts
  async function initAlerts(){ const desc=$('#rts-alert-descriptor'); const list=$('#rts-alerts-list'); const form=$('#rts-alert-form'); if (desc){ const d=await API.get('alerts/create/'); if (d) desc.textContent=(d.description||'Create an alert'); }
    if (form){ form.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(form); const res=await API.post('alerts/create/', Object.fromEntries(fd.entries())); showToast(res && res.message ? res.message : 'Alert created', res && res.alert_id ? 'success' : 'error'); const msg=$('#rts-alert-msg'); if(msg) msg.textContent = res && res.message ? res.message : 'Done'; }); }
    if (list){ const data=await API.get('wordpress/alerts/'); if(data && data.data){ list.innerHTML = data.data.slice(0,20).map(a=>'<div class="border rounded p-2 flex justify-between"><span>'+a.ticker+' • '+a.alert_type+' '+a.target_value+'</span><span>'+(a.is_active?'Active':'Inactive')+'</span></div>').join(''); } }
  }

  // News
  async function initNews(){ const container=$('#rts-news'); const filterForm=$('#rts-news-filters'); if (!container) return; async function load(params){ setSkeleton(container,true); const data = await API.get('wordpress/news/', params||{}); setSkeleton(container,false); if(!data||!data.data){ container.textContent='No news'; return; } container.innerHTML = data.data.map(n=>'<article class="border rounded p-3"><a href="'+n.url+'" target="_blank" rel="noopener" class="font-semibold hover:underline">'+n.title+'</a><div class="text-sm text-muted-foreground mt-1">'+(n.source||'')+' • '+(n.published_at||'')+' • '+(n.sentiment||'')+'</div><p class="mt-2">'+(n.summary||'')+'</p></article>').join(''); }
    if (filterForm){ filterForm.addEventListener('submit', function(e){ e.preventDefault(); const fd=new FormData(filterForm); load(Object.fromEntries(fd.entries())); }); }
    load({ limit:'20' }); }

  // API Docs – use site origin
  async function initDocs(){ const container=$('#rts-api-docs'); if(!container) return; setSkeleton(container,true); const origin = apiOrigin(); let data=null; if (origin){ try{ const res = await fetch(origin + '/docs/', { credentials: 'include' }); if(res.ok){ const ct=res.headers.get('content-type')||''; data = ct.includes('application/json') ? await res.json() : null; } }catch(e){ /* ignore */ } } setSkeleton(container,false); if (data && data.endpoints){ container.innerHTML = data.endpoints.map(ep=>'<div class="border rounded p-2"><code>'+ep.method+' '+ep.path+'</code><div class="text-sm text-muted-foreground">'+(ep.description||'')+'</div></div>').join(''); } else { container.textContent='Docs not available. Configure API URL or provide docs endpoint.'; } }

  // Endpoint Status – use site origin
  async function initEndpointStatus(){ const container=$('#rts-endpoint-status'); if(!container) return; setSkeleton(container,true); const origin = apiOrigin(); let data=null; if (origin){ try{ const res = await fetch(origin + '/endpoint-status/', { credentials: 'include' }); if(res.ok){ const ct=res.headers.get('content-type')||''; data = ct.includes('application/json') ? await res.json() : null; } }catch(e){ /* ignore */ } } setSkeleton(container,false); if (!data || !data.success){ container.textContent='No data'; return; } const list = data.data && data.data.endpoints ? data.data.endpoints : []; container.innerHTML = '<div class="overflow-x-auto rounded-lg border">\n<table class="min-w-full text-sm"><thead class="bg-muted/50 text-muted-foreground"><tr><th class="px-3 py-2 text-left">Name</th><th class="px-3 py-2 text-left">URL</th><th class="px-3 py-2 text-left">Status</th><th class="px-3 py-2 text-left">Code</th><th class="px-3 py-2 text-left">Response (ms)</th></tr></thead><tbody>'+ list.map(e => '<tr class="border-t"><td class="px-3 py-2">'+(e.name||'')+'</td><td class="px-3 py-2">'+(e.url||'')+'</td><td class="px-3 py-2">'+(e.status||'')+'</td><td class="px-3 py-2">'+(e.status_code||'')+'</td><td class="px-3 py-2">'+(e.response_time||'')+'</td></tr>').join('') + '</tbody></table></div>'; }

  // Footer subscribe override (optional)
  function initSubscribe(){ const form=$('#rts-subscribe-form'); if(!form) return; form.addEventListener('submit', async function(e){ if(!apiBase) return; e.preventDefault(); const fd=new FormData(form); const email=fd.get('email'); if(!email) return; const res = await API.post('subscription/', { email }); const note = $('#rts-subscribe-note'); if(note){ note.textContent = (res&&res.success)?'Thanks for subscribing!':'Subscription failed.'; note.className = 'notice ' + ((res&&res.success)?'notice-success':'notice-error'); } showToast((res&&res.success)?'Subscribed':'Subscribe failed', (res&&res.success)?'success':'error'); }); }

  document.addEventListener('DOMContentLoaded', function(){
    notifyMissingApi();
    initHealthIndicator();
    initDashboard();
    initScanner();
    initWatchlists();
    initPortfolio();
    initAlerts();
    initNews();
    initDocs();
    initEndpointStatus();
    initSubscribe();
  });
})(window, document);