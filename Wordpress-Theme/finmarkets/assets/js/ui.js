(function(){
  // Theme + auth + redirects + header behavior
  const $ = s => document.querySelector(s);
  const body = document.body;
  function getUser(){ try { return JSON.parse(localStorage.getItem('finm_user')||'null'); } catch(e){ return null; } }
  function isSignedIn(){ return !!getUser(); }

  // Set guest/signed-in class for conditional UI
  function applyAuthClasses(){ body.classList.toggle('guest', !isSignedIn()); body.classList.toggle('signed', !!isSignedIn()); }

  // Redirect rules
  function redirects(){
    const isHome = body.classList.contains('home');
    const requiresAuth = (body.getAttribute('data-requires-auth') === 'true');
    if (isHome && isSignedIn()) { window.location.href = (window.finmDashboardUrl || '/dashboard'); return; }
    if (requiresAuth && !isSignedIn()) { /* keep minimal header visible; optionally soft redirect */ }
  }

  // Header search behavior: expand on icon click
  function bindSearch(){
    const f = document.querySelector('.search');
    if(!f) return;
    const input = f.querySelector('.search-input');
    const btn = f.querySelector('.search-btn');
    btn.addEventListener('click', (e)=>{ if(document.activeElement !== input){ e.preventDefault(); input.focus(); } });
    input.addEventListener('blur', ()=>{ /* CSS handles collapse via :focus-within */ });
  }

  // Theme toggle
  function themeInit(){
    const pref = localStorage.getItem('finm_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(pref);
    $('#themeToggle')?.addEventListener('click',()=>{ setTheme(document.documentElement.classList.contains('dark') ? 'light' : 'dark'); });
  }
  function setTheme(mode){ document.documentElement.classList.toggle('dark', mode==='dark'); localStorage.setItem('finm_theme', mode); const btn=$('#themeToggle'); if(btn) btn.textContent = mode==='dark' ? 'Light Theme' : 'Dark Theme'; }

  // Header CTA: Sign up link visibility
  function headerCta(){ const link=$('#signupLink'); if(link){ link.style.display = isSignedIn() ? 'none':'inline-flex'; } }

  // Protected page banner visibility handled via CSS + body classes

  // Expose dashboard url
  window.finmDashboardUrl = window.finmDashboardUrl || '/dashboard';

  document.addEventListener('DOMContentLoaded', function(){
    applyAuthClasses();
    redirects();
    bindSearch();
    themeInit();
    headerCta();
  });
})();