(function(){
  // Small UI helpers for better polish + dark mode + keyboard shortcuts
  function smoothAnchors(){
    document.querySelectorAll('a[href^="#"]').forEach(a=>{
      a.addEventListener('click', e=>{
        const id=a.getAttribute('href');
        const el=id && document.querySelector(id);
        if(el){ e.preventDefault(); el.scrollIntoView({ behavior:'smooth', block:'start' }); }
      });
    });
  }

  function themeInit(){
    const pref = localStorage.getItem('finm_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(pref);
    const btn=document.getElementById('themeToggle');
    if(btn){
      btn.addEventListener('click',()=>{
        const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
        setTheme(next);
      });
    }
  }
  function setTheme(mode){
    document.documentElement.classList.toggle('dark', mode==='dark');
    localStorage.setItem('finm_theme', mode);
    const btn=document.getElementById('themeToggle');
    if(btn) btn.textContent = mode==='dark' ? 'Light Theme' : 'Dark Theme';
  }

  function shortcuts(){
    window.addEventListener('keydown', async (e)=>{
      if (e.target && (e.target.tagName==='INPUT' || e.target.tagName==='TEXTAREA' || e.target.isContentEditable)) return;
      // D - Dashboard
      if(e.key==='d' || e.key==='D'){ window.location.href = (window.finmDashboardUrl || '/'); }
      // W - Watchlist
      if(e.key==='w' || e.key==='W'){ const wl = document.querySelector('#watchlist') || document.querySelector('[href*="watchlist"]'); if(wl){ wl.scrollIntoView({behavior:'smooth'}); } }
      // Ctrl/Cmd + R - Refresh stock data via API
      if((e.ctrlKey||e.metaKey) && (e.key==='r' || e.key==='R')){
        e.preventDefault();
        try {
          const out = document.getElementById('refreshStatus'); if(out) out.textContent='Refreshing…';
          if(window.finmApi){ await window.finmApi.stocks({ limit: 50, sort_by: 'last_updated', sort_order: 'desc' }); }
          if(out) out.textContent='Refreshed';
        } catch(err){ const out=document.getElementById('refreshStatus'); if(out) out.textContent='Refresh failed'; }
      }
      // Esc - blur active element
      if(e.key==='Escape'){ if(document.activeElement) document.activeElement.blur(); }
    });

    // Show focus ring only when tabbing
    function handleFirstTab(ev){ if(ev.key==='Tab'){ document.body.classList.add('user-is-tabbing'); window.removeEventListener('keydown', handleFirstTab); } }
    window.addEventListener('keydown', handleFirstTab);
  }

  document.addEventListener('DOMContentLoaded', function(){
    smoothAnchors();
    themeInit();
    shortcuts();
  });
})();