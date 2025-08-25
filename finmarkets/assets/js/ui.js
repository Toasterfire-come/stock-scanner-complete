(function(){
  const $ = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));
  const body = document.body;
  function getUser(){ try { return JSON.parse(localStorage.getItem('finm_user')||'null'); } catch(e){ return null; } }
  function isSignedIn(){ return !!getUser(); }

  function ensureRequiresAuthHeuristic(){
    const val = body.getAttribute('data-requires-auth');
    if(val === 'true') return;
    const p = (location.pathname||'').toLowerCase();
    const protectedPatterns = ['dashboard','account','billing','checkout','subscriptions','settings','user-settings','notifications'];
    if (protectedPatterns.some(k => p.includes(k))) { body.setAttribute('data-requires-auth','true'); }
  }

  function applyAuthClasses(){ body.classList.toggle('guest', !isSignedIn()); body.classList.toggle('signed', !!isSignedIn()); }

  function redirects(){
    const isHome = body.classList.contains('home');
    const requiresAuth = (body.getAttribute('data-requires-auth') === 'true');
    if (isHome && isSignedIn()) { window.location.href = (window.finmDashboardUrl || '/dashboard'); return; }
  }

  function bindSearch(){ const f = $('.search'); if(!f) return; const input = f.querySelector('.search-input'); const btn = f.querySelector('.search-btn'); btn.addEventListener('click', (e)=>{ if(document.activeElement !== input){ e.preventDefault(); input.focus(); } }); }

  function themeInit(){ const pref = localStorage.getItem('finm_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); setTheme(pref); $('#themeToggle')?.addEventListener('click',()=>{ setTheme(document.documentElement.classList.contains('dark') ? 'light' : 'dark'); }); }
  function setTheme(mode){ document.documentElement.classList.toggle('dark', mode==='dark'); localStorage.setItem('finm_theme', mode); const btn=$('#themeToggle'); if(btn) btn.textContent = mode==='dark' ? 'Light Theme' : 'Dark Theme'; }

  function headerCta(){ const link=$('#signupLink'); if(link){ link.style.display = isSignedIn() ? 'none':'inline-flex'; } }

  // API connectivity guard + badge
  async function apiGuard(){
    const requiresApi = (body.getAttribute('data-requires-api') === 'true');
    const badge = $('#connBadge');
    async function setBadge(state){ if(!badge) return; badge.classList.remove('badge-green','badge-red'); if(state==='ok'){ badge.textContent='Connected'; badge.classList.add('badge-green'); } else if(state==='degraded'){ badge.textContent='Degraded'; badge.classList.add('badge-red'); } else { badge.textContent='Offline'; badge.classList.add('badge-red'); } }

    try{
      const path = (location.pathname||'').replace(/\/+/g,'/');
      if(path.startsWith('/backend-offline')){ await setBadge('offline'); return; }
      if(!(window.finmConfig && window.finmConfig.hasApiBase)) { await setBadge('offline'); if(requiresApi){ window.location.href = '/backend-offline/'; } return; }
      const controller = new AbortController(); const t = setTimeout(()=>controller.abort(), 3500);
      const r = await fetch(String(window.finmConfig.restBase||'/wp-json/finm/v1').replace(/\/$/,'') + '/health', { signal: controller.signal });
      clearTimeout(t);
      if(!r.ok){ await setBadge('offline'); if(requiresApi){ window.location.href = '/backend-offline/'; } return; }
      let j={}; try{ j = await r.json(); }catch(e){}
      const status = (j.status||'').toLowerCase();
      if(status==='healthy'){ await setBadge('ok'); }
      else { await setBadge('degraded'); if(requiresApi){ window.location.href = '/backend-offline/'; } }
    }catch(e){ await setBadge('offline'); if(requiresApi){ window.location.href = '/backend-offline/'; } }
  }

  function initPricing(){ const root = document.querySelector('[data-pricing-toggle]'); if(!root) return; root.addEventListener('click', ()=>{ document.body.classList.toggle('pricing-annual'); }); }
  function initAccordion(){ $$('.accordion .accordion-header').forEach(h=>{ h.addEventListener('click', ()=>{ const item=h.parentElement; item.classList.toggle('open'); }); }); }

  window.finmDashboardUrl = window.finmDashboardUrl || '/dashboard';

  document.addEventListener('DOMContentLoaded', function(){
    ensureRequiresAuthHeuristic();
    applyAuthClasses();
    redirects();
    bindSearch();
    themeInit();
    headerCta();
    initPricing();
    initAccordion();
    apiGuard();
  });
})();