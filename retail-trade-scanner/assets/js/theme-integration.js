(function(window, document){
  'use strict';
  const cfg = window.rtsConfig || {};
  const apiBaseRaw = (cfg.apiBase || '').trim();
  const apiBase = apiBaseRaw.endsWith('/') ? apiBaseRaw : apiBaseRaw + '/';
  const revenueBaseRaw = (cfg.revenueBase || (apiBase ? apiBase.replace(/\/api\/?$/, '/revenue/') : '')).trim();
  const revenueBase = revenueBaseRaw.endsWith('/') ? revenueBaseRaw : revenueBaseRaw + '/';

  function buildUrl(base, path){
    if (!base) return '';
    const p = path.replace(/^\//,'');
    return base + p;
  }

  async function fetchJson(url, opts){
    try{
      const res = await fetch(url, Object.assign({
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      }, opts||{}));
      if(!res.ok){ throw new Error('HTTP '+res.status); }
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('application/json')){
        return await res.json();
      }
      return await res.text();
    }catch(e){ console.warn('rts fetch failed', url, e); return null; }
  }

  // Health indicator (header)
  async function initHealthIndicator(){
    const dot = document.getElementById('rts-health-dot');
    if(!dot || !apiBase) return;
    const data = await fetchJson(buildUrl(apiBase, 'health/'));
    let color = '#f59e0b'; // amber default
    if (data && (data.status === 'healthy' || data.success === true)) color = '#10b981';
    if (!data) color = '#ef4444';
    dot.style.backgroundColor = color;
    dot.title = data ? ('API: '+(data.status||'ok')) : 'API: unreachable';
  }

  // Dashboard
  async function initDashboard(){
    const kpis = document.getElementById('rts-kpis');
    const gainers = document.getElementById('rts-trending-gainers');
    const active = document.getElementById('rts-trending-active');
    if(!kpis && !gainers && !active) return;
    if(apiBase){
      const stats = await fetchJson(buildUrl(apiBase, 'market-stats/'));
      if (kpis){
        if (stats && stats.market_overview){
          kpis.innerHTML = ''+
            '<div class="card"><div class="p-3"><div>Total Stocks</div><div class="text-lg">'+(stats.market_overview.total_stocks||'-')+'</div></div></div>'+
            '<div class="card"><div class="p-3"><div>Gainers</div><div class="text-lg">'+(stats.market_overview.gainers||'-')+'</div></div></div>'+
            '<div class="card"><div class="p-3"><div>Losers</div><div class="text-lg">'+(stats.market_overview.losers||'-')+'</div></div></div>'+
            '<div class="card"><div class="p-3"><div>Unchanged</div><div class="text-lg">'+(stats.market_overview.unchanged||'-')+'</div></div></div>';
        } else { kpis.textContent = 'No market data'; }
      }
      const trend = await fetchJson(buildUrl(apiBase, 'trending/'));
      function renderList(el, arr){
        if (!el) return; if(!arr||!arr.length){ el.textContent='No data'; return; }
        el.innerHTML = arr.slice(0,10).map(x => '<div class="border rounded p-2 flex justify-between"><span>'+(x.ticker||x.name)+'</span><span>'+(x.current_price||'-')+'</span></div>').join('');
      }
      if (trend){
        renderList(gainers, trend.top_gainers||trend.high_volume);
        renderList(active, trend.most_active);
      }
    }
  }

  // Scanner
  function initScanner(){
    const form = document.getElementById('rts-scanner-form');
    const results = document.getElementById('rts-scanner-results');
    const ac = document.getElementById('rts-search');
    if(!form || !results) return;
    async function runSearch(params){
      if(!apiBase) return;
      const url = new URL(buildUrl(apiBase, 'stocks/'));
      Object.keys(params).forEach(k => { if(params[k]!=='' && params[k]!==null && params[k]!==undefined) url.searchParams.set(k, params[k]); });
      const data = await fetchJson(url.toString());
      if(!data || data.success===false){ results.textContent='No results'; return; }
      const rows = (data.data||data.stocks||[]).slice(0,50).map(r => '<tr class="border-t">\n<td class="px-3 py-2">'+(r.ticker||r.symbol)+'</td>\n<td class="px-3 py-2">'+(r.company_name||r.name||'')+'</td>\n<td class="px-3 py-2">'+(r.current_price??'')+'</td>\n<td class="px-3 py-2">'+(r.change_percent??'')+'</td>\n</tr>').join('');
      results.innerHTML = '<div class="overflow-x-auto rounded-lg border">\n<table class="min-w-full text-sm"><thead class="bg-muted/50 text-muted-foreground"><tr><th class="px-3 py-2 text-left">Ticker</th><th class="px-3 py-2 text-left">Name</th><th class="px-3 py-2 text-left">Price</th><th class="px-3 py-2 text-left">Change %</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
    }
    form.addEventListener('submit', function(e){ e.preventDefault(); const fd = new FormData(form); const params = Object.fromEntries(fd.entries()); runSearch(params); });
    if (ac){ let t=null; ac.addEventListener('input', function(){ clearTimeout(t); t=setTimeout(async ()=>{
      if(!apiBase || !ac.value.trim()) return; const url = new URL(buildUrl(apiBase, 'search/')); url.searchParams.set('q', ac.value.trim()); const data = await fetchJson(url.toString());
      // Simple suggestion list
      const sug = document.getElementById('rts-autocomplete'); if (!sug) return; sug.innerHTML = (data&&data.results?data.results.slice(0,8):[]).map(r=>'<div class="px-2 py-1 hover:underline">'+(r.ticker||r.company_name)+'</div>').join('');
    }, 250); }); }
  }

  // Watchlists
  function initWatchlists(){
    const list = document.getElementById('rts-watchlist');
    const addForm = document.getElementById('rts-watchlist-add');
    async function load(){ if(!apiBase||!list) return; const data = await fetchJson(buildUrl(apiBase,'watchlist/')); if(!data||data.success===false){ list.textContent='No items'; return; } list.innerHTML=(data.data||[]).map(i=>'<div class="border rounded p-2 flex justify-between"><span>'+i.symbol+'</span><button data-id="'+i.id+'" class="rts-wl-del border rounded px-2">Remove</button></div>').join(''); }
    document.addEventListener('click', async (e)=>{ const btn=e.target.closest('.rts-wl-del'); if(!btn) return; e.preventDefault(); const id=btn.getAttribute('data-id'); await fetchJson(buildUrl(apiBase,'watchlist/'+id+'/'), { method:'DELETE' }); load(); });
    if(addForm){ addForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(addForm); const body=JSON.stringify(Object.fromEntries(fd.entries())); await fetchJson(buildUrl(apiBase,'watchlist/add/'), { method:'POST', body }); load(); }); }
    load();
  }

  // Portfolio
  function initPortfolio(){
    const list = document.getElementById('rts-portfolio');
    const addForm = document.getElementById('rts-portfolio-add');
    async function load(){ if(!apiBase||!list) return; const data = await fetchJson(buildUrl(apiBase,'portfolio/')); if(!data||data.success===false){ list.textContent='No holdings'; return; } const rows=(data.data||[]).map(h=>'<tr class="border-t"><td class="px-3 py-2">'+h.symbol+'</td><td class="px-3 py-2">'+h.shares+'</td><td class="px-3 py-2">'+h.avg_cost+'</td><td class="px-3 py-2">'+(h.current_price??'')+'</td><td class="px-3 py-2"><button data-id="'+h.id+'" class="rts-port-del border rounded px-2">Remove</button></td></tr>').join('');
      list.innerHTML = '<div class="overflow-x-auto rounded-lg border">\n<table class="min-w-full text-sm"><thead class="bg-muted/50 text-muted-foreground"><tr><th class="px-3 py-2 text-left">Symbol</th><th class="px-3 py-2 text-left">Shares</th><th class="px-3 py-2 text-left">Avg Cost</th><th class="px-3 py-2 text-left">Price</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>';
    }
    document.addEventListener('click', async (e)=>{ const btn=e.target.closest('.rts-port-del'); if(!btn) return; e.preventDefault(); const id=btn.getAttribute('data-id'); await fetchJson(buildUrl(apiBase,'portfolio/'+id+'/'), { method:'DELETE' }); load(); });
    if(addForm){ addForm.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(addForm); const body=JSON.stringify(Object.fromEntries(fd.entries())); await fetchJson(buildUrl(apiBase,'portfolio/add/'), { method:'POST', body }); load(); }); }
    load();
  }

  // Alerts
  async function initAlerts(){
    const desc = document.getElementById('rts-alert-descriptor');
    const list = document.getElementById('rts-alerts-list');
    const form = document.getElementById('rts-alert-form');
    if (desc && apiBase){ const d = await fetchJson(buildUrl(apiBase, 'alerts/create/')); if (d) desc.textContent = (d.description||'Create an alert'); }
    if (form){ form.addEventListener('submit', async (e)=>{ e.preventDefault(); const fd=new FormData(form); const body=JSON.stringify(Object.fromEntries(fd.entries())); const res=await fetchJson(buildUrl(apiBase,'alerts/create/'), { method:'POST', body }); const msg=document.getElementById('rts-alert-msg'); if(msg) msg.textContent = res && (res.message||'Created'); }); }
    if (list && apiBase){ const data = await fetchJson(buildUrl(apiBase,'wordpress/alerts/')); if(data && data.data){ list.innerHTML = data.data.slice(0,20).map(a=>'<div class="border rounded p-2 flex justify-between"><span>'+a.ticker+' • '+a.alert_type+' '+a.target_value+'</span><span>'+(a.is_active?'Active':'Inactive')+'</span></div>').join(''); } }
  }

  // News
  async function initNews(){
    const container = document.getElementById('rts-news');
    const filterForm = document.getElementById('rts-news-filters');
    if (!container) return;
    async function load(params){ if(!apiBase) return; const url = new URL(buildUrl(apiBase,'wordpress/news/')); Object.keys(params||{}).forEach(k=>{ if(params[k]) url.searchParams.set(k, params[k]); }); const data = await fetchJson(url.toString()); if(!data||!data.data){ container.textContent='No news'; return; } container.innerHTML = data.data.map(n=>'<article class="border rounded p-3"><a href="'+n.url+'" target="_blank" rel="noopener" class="font-semibold hover:underline">'+n.title+'</a><div class="text-sm text-muted-foreground mt-1">'+(n.source||'')+' • '+(n.published_at||'')+'</div><p class="mt-2">'+(n.summary||'')+'</p></article>').join(''); }
    if (filterForm){ filterForm.addEventListener('submit', function(e){ e.preventDefault(); const fd=new FormData(filterForm); load(Object.fromEntries(fd.entries())); }); }
    load({ limit: '20' });
  }

  // API Docs
  async function initDocs(){
    const container = document.getElementById('rts-api-docs'); if(!container) return;
    if (apiBase){ const res = await fetchJson(buildUrl(apiBase, '../docs/')); if (res && res.endpoints){ container.innerHTML = res.endpoints.map(ep=>'<div class="border rounded p-2"><code>'+ep.method+' '+ep.path+'</code><div class="text-sm text-muted-foreground">'+(ep.description||'')+'</div></div>').join(''); return; } }
    container.textContent = 'Docs not available. Configure API URL or provide docs endpoint.';
  }

  // Endpoint Status
  async function initEndpointStatus(){
    const container = document.getElementById('rts-endpoint-status'); if(!container||!apiBase) return;
    const data = await fetchJson(buildUrl(apiBase, '../endpoint-status/'));
    if (!data || !data.success){ container.textContent='No data'; return; }
    const list = data.data && data.data.endpoints ? data.data.endpoints : [];
    container.innerHTML = list.map(e => '<div class="border rounded p-2 flex justify-between"><span>'+e.name+'</span><span>'+(e.status||'')+' • '+(e.status_code||'')+' • '+(e.response_time||'')+'ms</span></div>').join('');
  }

  // Footer subscribe override (optional)
  function initSubscribe(){
    const form = document.getElementById('rts-subscribe-form'); if(!form || !apiBase) return;
    form.addEventListener('submit', async function(e){ e.preventDefault(); const fd=new FormData(form); const email=fd.get('email'); if(!email) return; const body=JSON.stringify({ email: email }); const res = await fetchJson(buildUrl(apiBase,'subscription/'), { method:'POST', body }); const note = document.getElementById('rts-subscribe-note'); if(note){ note.textContent = (res&&res.success)?'Thanks for subscribing!':'Subscription failed.'; note.className = 'notice ' + ((res&&res.success)?'notice-success':'notice-error'); }
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
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