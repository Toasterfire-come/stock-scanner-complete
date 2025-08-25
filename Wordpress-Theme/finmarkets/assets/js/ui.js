(function(){
  const $ = s => document.querySelector(s);
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
    // For protected pages we keep a minimal header (home icon) without auto-redirect to allow navigation back
  }

  function bindSearch(){
    const f = document.querySelector('.search'); if(!f) return;
    const input = f.querySelector('.search-input'); const btn = f.querySelector('.search-btn');
    btn.addEventListener('click', (e)=>{ if(document.activeElement !== input){ e.preventDefault(); input.focus(); } });
  }

  function themeInit(){
    const pref = localStorage.getItem('finm_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(pref);
    $('#themeToggle')?.addEventListener('click',()=>{ setTheme(document.documentElement.classList.contains('dark') ? 'light' : 'dark'); });
  }
  function setTheme(mode){ document.documentElement.classList.toggle('dark', mode==='dark'); localStorage.setItem('finm_theme', mode); const btn=$('#themeToggle'); if(btn) btn.textContent = mode==='dark' ? 'Light Theme' : 'Dark Theme'; }

  function headerCta(){ const link=$('#signupLink'); if(link){ link.style.display = isSignedIn() ? 'none':'inline-flex'; } }

  window.finmDashboardUrl = window.finmDashboardUrl || '/dashboard';

  document.addEventListener('DOMContentLoaded', function(){
    ensureRequiresAuthHeuristic();
    applyAuthClasses();
    redirects();
    bindSearch();
    themeInit();
    headerCta();
  });
})();